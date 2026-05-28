from types import SimpleNamespace
from typing import Any, cast

from packages.core.bootstrap_runtime.concurrency.safe_executor import SafeExecutor as Executor
from packages.core.bootstrap_runtime.runtime_scope import RuntimeScopeManager
from packages.core.runtime_config.loader import load_settings
from packages.features.dice_engine import (
    DiceUseCase,
    DomainDiceDistributionAnalyzerAdapter,
    DomainDiceParserAdapter,
    DomainDiceRollerAdapter,
)
from packages.features.embedding_gateway.contracts import (
    EmbeddingGatewayContract as EmbeddingGateway,
)
from packages.features.llm_gateway.application.llm_service import LLMService
from packages.features.llm_gateway.contracts import LLMGatewayContract
from packages.features.llm_gateway.infrastructure.provider_factory import create_llm_provider
from packages.features.prompt_engine_core.session_summarizer import SessionSummarizer
from packages.features.rpg_engine import (
    EndSessionUseCase,
    NarrativeUseCase,
)
from packages.features.rpg_engine.context_builder import ContextBuilder
from packages.features.rpg_engine.infrastructure.narrative_memory_repository import (
    NarrativeMemoryRepository,
)
from packages.features.rpg_engine.memory_service import MemoryService
from packages.features.semantic_cache.implementations import EmbeddingCache, SemanticCache
from packages.features.storage import (
    CampaignStorageProviderContract,
    CampaignStorageService,
    LegacyCampaignStorageFactory,
)
from packages.features.vector_index.contracts import VectorReaderPort, VectorWriterPort
from packages.features.vector_index.reader import VectorReaderService
from packages.features.vector_index.writer import VectorWriterService
from semantic_context_server.application.dispatch.application_registry import ApplicationRegistry
from semantic_context_server.application.ports.event_bus import EventBus as EventBusPort

# Ports
from semantic_context_server.application.ports.executor import ExecutorPort
from semantic_context_server.application.runtime.campaign_runtime import CampaignRuntime
from semantic_context_server.bootstrap.container import Container
from semantic_context_server.infrastructure.events.blinker_event_bus import BlinkerEventBus
from semantic_context_server.infrastructure.random.default_random import DefaultRandomProvider

# Infra
from semantic_context_server.infrastructure.runtime.bus.event_bus import EventBus as AsyncEventBus


class _CampaignAdapter:
    """Backward-compat single-arg campaign API backed by RuntimeScopeManager."""

    def __init__(self, scope_manager: RuntimeScopeManager) -> None:
        self._scope_manager = scope_manager

    async def get(self, campaign_id: str) -> Any:
        return await self._scope_manager.get("rpg", f"campaign:{campaign_id}")

    async def clear(self, campaign_id: str) -> None:
        await self._scope_manager.clear("rpg", f"campaign:{campaign_id}")

    async def shutdown(self) -> None:
        await self._scope_manager.shutdown()


class _DictKV:
    """Minimal in-memory async KV used to back per-campaign caches."""

    def __init__(self) -> None:
        self._d: dict[str, Any] = {}

    async def get(self, key: str) -> Any:
        return self._d.get(key)

    async def set(self, key: str, value: Any) -> None:
        self._d[key] = value

    async def delete(self, key: str) -> None:
        self._d.pop(key, None)

    async def clear(self) -> None:
        self._d.clear()


class ContainerBuilder:
    """Fluent builder for the DI container.

    Compat shim — to be removed after BOOTSTRAP_RUNTIME=v2 is default.
    """

    def __init__(self) -> None:
        self._llm: Any | None = None
        self._embedding: Any | None = None
        self._executor: Any | None = None

    # ── fluent API ────────────────────────────────────────────

    def with_llm(self, llm: Any) -> "ContainerBuilder":
        self._llm = llm
        return self

    def with_embedding(self, embedding: Any) -> "ContainerBuilder":
        self._embedding = embedding
        return self

    def with_executor(self, executor: Any) -> "ContainerBuilder":
        self._executor = executor
        return self

    # ── build ─────────────────────────────────────────────────

    def _build_semantic_cache(self) -> Any:
        try:
            from packages.features.semantic_cache import LegacySemanticCacheAdapter

            return LegacySemanticCacheAdapter()
        except ModuleNotFoundError:
            return SemanticCache(kv_store=_DictKV())

    def _build_storage_provider(self, storage_config: Any, executor: ExecutorPort) -> Any:
        from semantic_context_server.infrastructure.storage.campaign_storage_factory import (
            build_campaign_storage,
        )

        factory = LegacyCampaignStorageFactory(
            storage_config,
            executor,
            builder=build_campaign_storage,
        )
        return CampaignStorageService(factory)

    def build(
        self,
        campaign_id: str | None = None,
        storage_config: Any | None = None,
        base_path: str | None = None,
    ) -> Container:
        container = Container()
        container.settings = load_settings()
        container.run_benchmark = None

        # Core infra
        executor = self._executor or Executor()
        container.register(ExecutorPort, executor)
        event_bus = BlinkerEventBus()
        container.register(EventBusPort, event_bus)
        container.event_bus = event_bus
        async_event_bus = AsyncEventBus()
        container.register(AsyncEventBus, async_event_bus)

        llm = self._llm if self._llm is not None else self._build_llm()
        container.register(LLMGatewayContract, llm)
        container.llm = llm
        if self._embedding is not None:
            container.register(EmbeddingGateway, self._embedding)
        container.embedding = self._embedding

        # Application registry
        app_registry = ApplicationRegistry()
        container.application_registry = app_registry
        container.register(ApplicationRegistry, app_registry)

        # Storage provider
        storage_provider = self._build_storage_provider(
            storage_config, cast(ExecutorPort, executor)
        )
        container.register(CampaignStorageProviderContract, storage_provider)

        # Campaign factory
        async def build_campaign(cid: str) -> CampaignRuntime:
            provider = container.resolve(CampaignStorageProviderContract)
            ctx = SimpleNamespace(
                id=cid,
                kv=provider.get(cid),
            )
            services: dict = {
                "llm": container.resolve(LLMGatewayContract),
                "storage": ctx.kv,
                "command_bus": container.command_bus,
                "embedding": self._embedding,
            }
            # --- RAG (vector reader / writer) ---
            try:
                reader_index = container.resolve(VectorReaderPort)
                writer_index = container.resolve(VectorWriterPort)
                services["vector_reader"] = VectorReaderService(vector_index=reader_index)
                services["vector_writer"] = VectorWriterService(
                    vector_index=writer_index, managed=True
                )
                services["vector_index"] = writer_index
            except KeyError:

                class _NullVectorReader:
                    async def search(  # noqa: ARG002
                        self,
                        campaign_id: str,
                        query: str,
                        k: int = 5,
                        filters: dict[str, Any] | None = None,
                    ) -> list[dict[str, Any]]:
                        return []

                class _NullVectorWriter:
                    async def store_event(  # noqa: ARG002
                        self, campaign_id: str, texts: list[str], metadata: dict
                    ) -> None:
                        return None

                class _NullVectorIndex:
                    def __init__(self) -> None:
                        class _NullDocumentStore:
                            async def get(self, key: str) -> dict | None:  # noqa: ARG002
                                return None

                        self.raw = SimpleNamespace(
                            components=SimpleNamespace(
                                vector_writer=_NullVectorWriter(),
                                vector_reader=_NullVectorReader(),
                                document_store=_NullDocumentStore(),
                            )
                        )

                    async def index_campaign(  # noqa: ARG002
                        self,
                        campaign_id: str,
                        texts: list[str],
                        metadata: dict[str, Any] | None = None,
                    ) -> None:
                        return None

                    async def search(self, query: str, k: int = 4) -> list[dict]:  # noqa: ARG002
                        return []

                    async def search_with_metadata(self, query: str, k: int = 4) -> list[dict]:  # noqa: ARG002
                        return []

                services["vector_reader"] = _NullVectorReader()
                services["vector_writer"] = _NullVectorWriter()
                services["vector_index"] = _NullVectorIndex()

            # --- Memory ---
            kv_backend = ctx.kv
            if hasattr(kv_backend, "build_kv_store"):
                kv_store = kv_backend.build_kv_store("narrative_memory")
            else:
                kv_store = kv_backend.build_document_store()
            services["memory"] = MemoryService(
                repository=NarrativeMemoryRepository(kv_store),
                campaign_id=ctx.id,
                summarizer=SessionSummarizer(),
                llm_service=container.resolve(LLMGatewayContract),
                executor=container.resolve(ExecutorPort),
                vector_reader=services.get("vector_reader"),
                vector_writer=services.get("vector_writer"),
                narrative_graph=services.get("narrative_graph"),
            )

            # --- Narrative ---
            _memory = services["memory"]
            services["narrative"] = NarrativeUseCase(
                llm=container.resolve(LLMGatewayContract),
                memory_service=_memory,
                context_builder=ContextBuilder(memory_service=_memory),
            )
            services["embedding_cache"] = EmbeddingCache(kv_store=_DictKV(), client=self._embedding)
            services["semantic_cache"] = self._build_semantic_cache()
            services["roll_dice"] = DiceUseCase(
                rng=DefaultRandomProvider(),
                parser=DomainDiceParserAdapter(),
                roller=DomainDiceRollerAdapter(),
                analyzer=DomainDiceDistributionAnalyzerAdapter(),
                executor=container.resolve(ExecutorPort),
                enable_analysis=False,
            )
            services["end_session"] = EndSessionUseCase(
                memory_service=services["memory"],
                llm=services["llm"],
                vector_writer=services["vector_writer"],
                executor=container.resolve(ExecutorPort),
            )
            return CampaignRuntime(cid, services)

        async def _build_scope_runtime(_world_id: str, scope_id: str) -> CampaignRuntime:
            return await build_campaign(scope_id.removeprefix("campaign:"))

        scope_manager = RuntimeScopeManager(
            builder=SimpleNamespace(build_scope_runtime=_build_scope_runtime)
        )
        container.campaigns = _CampaignAdapter(scope_manager)

        # Lifecycle helpers
        async def _start() -> None:
            app_registry.configure(container)

        async def _shutdown() -> None:
            await async_event_bus.shutdown()
            exc: ExecutorPort = container.resolve(ExecutorPort)
            await exc.shutdown()

        container.start = _start
        container.shutdown = _shutdown

        # command_bus — global bus (per-campaign buses live on CampaignRuntime)
        from semantic_context_server.application.commands.command_bus import CommandBus

        container.command_bus = CommandBus(registry={})

        return container

    def _build_llm(self) -> Any:
        settings = load_settings()
        try:
            provider = create_llm_provider(settings.llm)
        except Exception as exc:  # pragma: no cover - explicit startup guard
            raise RuntimeError(
                f"Failed to build LLM provider for '{settings.llm.provider}'. "
                "Set a valid LLM_PROVIDER/LLM_MODEL configuration."
            ) from exc

        return LLMService(provider=provider, timeout=float(settings.llm.timeout))

    # ── legacy tuple API (used by lifecycle.py) ───────────────

    def build_tuple(self) -> tuple["Container", RuntimeScopeManager]:
        container = self.build()
        adapter: _CampaignAdapter = container.campaigns  # type: ignore[assignment]
        return container, adapter._scope_manager
