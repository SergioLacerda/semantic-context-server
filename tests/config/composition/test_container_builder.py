import tempfile
import uuid
from dataclasses import replace
from pathlib import Path

from packages.features.embedding_gateway.contracts import (
    EmbeddingGatewayContract as EmbeddingGateway,
)
from packages.features.llm_gateway.contracts import LLMGatewayContract
from semantic_context_server.application.ports.interaction_runtime import InteractionRuntimePort
from semantic_context_server.application.ports.storage_types import (
    StorageBackends,
    StorageKinds,
)
from semantic_context_server.bootstrap.container import Container
from semantic_context_server.bootstrap.container_builder import ContainerBuilder
from semantic_context_server.infrastructure.runtime.lifecycle.lifecycle_guard import LifecycleGuard
from tests.config.factories.state import _State
from tests.config.fakes.application.context.fake_context_service import FakeContextService
from tests.config.fakes.application.intent.fake_intent_classifier import FakeIntentClassifier
from tests.config.fakes.application.intent.fake_llm_intent_classifier import FakeLLMIntentClassifier
from tests.config.fakes.application.memory.fake_application_memory_service import (
    FakeApplicationMemoryService,
)
from tests.config.fakes.fake_time_provider import FakeTimeProvider
from tests.config.fakes.infrastructure.embedding.fake_embedding_provider import (
    FakeEmbeddingProvider,
)
from tests.config.fakes.infrastructure.llm.fake_llm_service import FakeLLMService
from tests.config.fakes.infrastructure.storage.fake_storage_config import FakeStorageConfig


class ContainerTestFactory:
    """
    Builder de container para testes (ALINHADO COM NOVA ARQUITETURA).

    ✔ Injeta fakes obrigatórios
    ✔ Compatível com ContainerBuilder real
    ✔ Isolamento total de infra
    ✔ Determinístico
    ✔ NÃO executa lifecycle automaticamente
    """

    def __init__(self, state: _State | None = None):
        if state is None:
            campaign_id = "test"

            state = _State(
                campaign_id=campaign_id,
                llm=FakeLLMService(),
                embedding=FakeEmbeddingProvider(),
                context=FakeContextService(),
                memory=FakeApplicationMemoryService(),
                intent=FakeIntentClassifier(llm_classifier=FakeLLMIntentClassifier()),
                base_path=self._build_path(campaign_id),
                time_provider=FakeTimeProvider(),
            )

        self._state = state

    # -----------------------------------------------------
    # PATH
    # -----------------------------------------------------

    def _build_path(self, campaign_id: str) -> str:
        tmp = Path(tempfile.gettempdir())
        return str(tmp / f"rpg_test_{campaign_id}_{uuid.uuid4().hex[:8]}")

    # -----------------------------------------------------
    # FLUENT API
    # -----------------------------------------------------

    def with_campaign(self, campaign_id: str):
        return ContainerTestFactory(
            replace(
                self._state,
                campaign_id=campaign_id,
                base_path=self._build_path(campaign_id),
            )
        )

    def with_llm(self, llm: FakeLLMService):
        return ContainerTestFactory(replace(self._state, llm=llm))

    def with_context(self, context: FakeContextService):
        return ContainerTestFactory(replace(self._state, context=context))

    def with_memory(self, memory: FakeApplicationMemoryService):
        return ContainerTestFactory(replace(self._state, memory=memory))

    def with_intent(self, intent: FakeIntentClassifier):
        return ContainerTestFactory(replace(self._state, intent=intent))

    # -----------------------------------------------------
    # STORAGE CONFIG
    # -----------------------------------------------------

    def _default_storage_config(self, namespace: str) -> FakeStorageConfig:
        return FakeStorageConfig(
            backends={
                StorageKinds.KV: StorageBackends.MEMORY,
                StorageKinds.VECTOR: StorageBackends.MEMORY,
                StorageKinds.DOCUMENT: StorageBackends.MEMORY,
                StorageKinds.METADATA: StorageBackends.MEMORY,
            },
            namespace=namespace,
        )

    # -----------------------------------------------------
    # BUILD
    # -----------------------------------------------------

    def build(
        self,
        *,
        storage_config=None,
        **overrides,
    ) -> Container:

        if storage_config is None:
            storage_config = self._default_storage_config(self._state.base_path)

        # ✔ World Class: Utilizamos o builder real para garantir a ordem correta
        # de bootstrap (Runtime -> Registry -> Storage).
        builder = ContainerBuilder().with_llm(self._state.llm).with_embedding(self._state.embedding)

        # Se o estado tiver um executor especializado (ex: FaultyExecutor), injetamos.
        # Caso contrário, o builder usará o padrão definido no RuntimeModule.
        executor = getattr(self._state, "executor", None)
        if executor is not None:
            builder = builder.with_executor(executor)

        container = builder.build(
            campaign_id=self._state.campaign_id,
            storage_config=storage_config,
            base_path=self._state.base_path,
        )

        # -------------------------------------------------
        # 🔥 LIFECYCLE GUARD (World Class Detection)
        # -------------------------------------------------
        guard = LifecycleGuard()
        container._lifecycle_guard = guard

        # Garantimos que o registro de aplicação esteja ciente dos fakes
        # para passar na validação de Async Mandate.
        registry = container.application_registry

        # ✔ World Class: Blindagem contra configurações acidentais de .env
        time_provider = getattr(self._state, "time_provider", None)
        overrides_map = {
            LLMGatewayContract: self._state.llm,
            EmbeddingGateway: self._state.embedding,
            InteractionRuntimePort: time_provider,
        }

        for port, impl in overrides_map.items():
            if impl:
                # Forçamos o override no registro de dependências
                container._registry.register(port, impl)

                name = impl.__class__.__name__
                registry.register_storage(name, impl)

        # -------------------------------------------------
        # 🔥 GARANTIA: LLM fake
        # -------------------------------------------------

        llm = container.resolve(LLMGatewayContract)

        assert "Fake" in type(llm).__name__, f"🚨 LLM real detectado: {type(llm)}"

        registry.validate()

        return container
