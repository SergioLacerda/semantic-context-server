from types import SimpleNamespace
from typing import Any, cast

from packages.features.embedding_gateway.contracts import (
    EmbeddingGatewayContract as EmbeddingGateway,
)
from packages.features.llm_gateway.application.llm_service import LLMService
from packages.features.llm_gateway.contracts import LLMGatewayContract
from packages.features.llm_gateway.infrastructure.provider_factory import create_llm_provider
from packages.features.rpg_engine import (
    DiceUseCase,
    DomainDiceDistributionAnalyzerAdapter,
    DomainDiceParserAdapter,
    DomainDiceRollerAdapter,
)
from packages.features.semantic_cache.implementations import EmbeddingCache, SemanticCache
from packages.features.storage import (
    CampaignStorageProviderContract,
    CampaignStorageService,
    LegacyCampaignStorageFactory,
)
from semantic_context_server.application.dispatch.application_registry import ApplicationRegistry
from semantic_context_server.application.ports.event_bus import EventBus as EventBusPort

# Ports
from semantic_context_server.application.ports.executor import ExecutorPort
from semantic_context_server.application.runtime.campaign_manager import CampaignManager
from semantic_context_server.application.runtime.campaign_runtime import CampaignRuntime
from semantic_context_server.application.usecases.end_session_usecase import EndSessionUseCase
from semantic_context_server.bootstrap.container import Container
from semantic_context_server.config.loader import load_settings
from semantic_context_server.infrastructure.events.blinker_event_bus import BlinkerEventBus
from semantic_context_server.infrastructure.random.default_random import DefaultRandomProvider

# Infra
from semantic_context_server.infrastructure.runtime.bus.event_bus import EventBus as AsyncEventBus
from semantic_context_server.infrastructure.runtime.executor.executor import Executor
from semantic_context_server.modules.memory_module import MemoryModule
from semantic_context_server.modules.narrative_module import NarrativeModule
from semantic_context_server.modules.rag_module import RAGModule


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
    """Fluent builder for the DI container."""

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
        factory = LegacyCampaignStorageFactory(storage_config, executor)
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
            services.update(RAGModule.build(container, ctx))
            services["memory"] = MemoryModule.build(container, ctx, services)
            services["narrative"] = NarrativeModule.build(container, ctx, services)
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

        manager = CampaignManager(builder=SimpleNamespace(build_campaign=build_campaign))
        container.campaigns = manager

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

    def build_tuple(self) -> tuple["Container", Any]:
        container = self.build()
        return container, container.campaigns
