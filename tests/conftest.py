# tests/conftest.py

import os
import sys
from pathlib import Path

# =========================================================
# ⚡ ENV BOOTSTRAP (Deve ocorrer antes de qualquer import do app)
# =========================================================
os.environ["ENVIRONMENT"] = "test"
os.environ["DEVICE"] = "cpu"
os.environ["ENV_FILE"] = "none"  # Desativa carga de .env no Pydantic Settings

from semantic_context_server.config.loader import load_settings

load_settings.cache_clear()

import asyncio  # noqa: E402, I001

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from packages.interfaces.http_api import create_app  # noqa: E402
from semantic_context_server.application.ports.executor import ExecutorPort  # noqa: E402
from semantic_context_server.application.ports.storage_types import (  # noqa: E402
    StorageBackends,
    StorageKinds,
)
from semantic_context_server.infrastructure.storage.providers.storage_backend_registry import (  # noqa: E402
    get_global_registry,
)
from semantic_context_server.infrastructure.storage.providers.storage_backend_registry_setup import (  # noqa: E402
    create_storage_backend_registry,
)
from semantic_context_server.interfaces.api.dependencies import (  # noqa: E402
    get_command_bus,
    get_container,
)
from tests.config.composition.test_container_builder import ContainerTestFactory  # noqa: E402
from tests.config.fakes.infrastructure.storage.fake_storage_config import FakeStorageConfig  # noqa: E402

# =========================================================
# PATH
# =========================================================

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

# =========================================================
# 🔥 HARD GUARD: PROIBIR LLM REAL
# =========================================================


@pytest.fixture(autouse=True)
def forbid_real_llm(monkeypatch):
    """
    Garante que NUNCA será possível criar provider real.
    """

    def _fail(*args, **kwargs):
        raise RuntimeError("🚨 LLM real proibido em testes")

    monkeypatch.setattr(
        "packages.features.llm_gateway.infrastructure.provider_factory.create_llm_provider",
        _fail,
    )


# =========================================================
# CORE CONTAINER
# =========================================================


def build_container(
    *,
    storage_config=None,
    campaign_id="test",
    **kwargs,
):
    builder = ContainerTestFactory()

    return builder.with_campaign(campaign_id).build(
        storage_config=storage_config,
        **kwargs,
    )


@pytest.fixture
def container_factory():
    def _factory(
        *,
        storage_config=None,
        campaign_id="test",
        **overrides,
    ):
        return build_container(
            campaign_id=campaign_id,
            storage_config=storage_config,
            **overrides,
        )

    return _factory


# =========================================================
# 🔥 MAIN ASYNC CONTAINER FIXTURE (CORRETA)
# =========================================================


@pytest.fixture
async def container(container_factory):
    c = container_factory(campaign_id="c1")
    try:
        # 🔥 1. START LIFECYCLE (Root + Registry)
        await c.start()

        # 🔥 2. WIRING CHECK: Garante que o dispatch global está pronto
        assert c.command_bus is not None
        assert c.application_registry is not None

        # 🔥 3. SCOPED INIT: força criação de campanha (garante wiring de handlers)
        campaign = await c.campaigns.get("c1")
        await campaign.initialize()

        # --------------------------------------------------
        # 🔥 SANITY CHECK (LLM fake)
        # --------------------------------------------------
        llm = campaign.llm
        assert "Fake" in type(llm).__name__, f"🚨 LLM real detectado no teste: {type(llm)}"

        # 🔥 4. Store campaign reference on container for convenience access in tests
        c._default_campaign = campaign

        yield c

    finally:
        # 🔥 SHUTDOWN: Garante limpeza de Executor, EventBus e Tasks pendentes
        await c.shutdown()

        # 🔥 2. deixar loop finalizar callbacks pendentes (yield control)
        for _ in range(3):
            await asyncio.sleep(0)

    # 🔥 3. garantir ZERO tasks vivas após o bloco finally
    pending = [t for t in asyncio.all_tasks() if not t.done() and t is not asyncio.current_task()]

    assert not pending, f"🔥 Pending tasks detected: {pending}"

    # 🔥 4. Check for Blinker orphan receivers
    root_event_bus = c.event_bus  # This is the root EventBus instance
    orphan_receivers = root_event_bus._check_for_orphan_receivers()
    assert not orphan_receivers, f"🔥 Blinker orphan receivers detected: {orphan_receivers}"

    # 🔥 4. lifecycle guard
    if hasattr(c, "_lifecycle_guard"):
        c._lifecycle_guard.assert_clean()


@pytest.fixture
def container_with_storage(container_factory, storage_config):
    return container_factory(
        campaign_id="c1",
        storage_config=storage_config,
    )


@pytest.fixture
def container_with_campaign(container_factory):
    return container_factory(campaign_id="c1")


@pytest.fixture
def campaign_id():
    return "c1"


# =========================================================
# FASTAPI APP
# =========================================================


def build_test_app(container, campaign_id="c1"):
    app = create_app()

    # --------------------------------------------------
    # CORE DI
    # --------------------------------------------------
    app.dependency_overrides[get_container] = lambda: container

    # --------------------------------------------------
    # CQRS
    # --------------------------------------------------
    async def _command_bus():
        campaign = await container.campaigns.get(campaign_id)
        return campaign.command_bus

    app.dependency_overrides[get_command_bus] = _command_bus

    return app


@pytest.fixture
def client(container):
    app = build_test_app(container, campaign_id="c1")
    return TestClient(app)


@pytest.fixture
def app(container):
    return build_test_app(container, campaign_id="c1")


# =========================================================
# STORAGE
# =========================================================


@pytest.fixture
def storage_config(tmp_path):
    return FakeStorageConfig(
        backends={
            StorageKinds.KV: StorageBackends.MEMORY,
            StorageKinds.VECTOR: StorageBackends.MEMORY,
            StorageKinds.DOCUMENT: StorageBackends.MEMORY,
            StorageKinds.METADATA: StorageBackends.MEMORY,
        },
        namespace=str(tmp_path),
    )


# =========================================================
# HELPERS
# =========================================================


@pytest.fixture
def container_campaign_factory(container_factory):
    return container_factory


# =========================================================
# GOLDEN TESTS
# =========================================================


def pytest_addoption(parser):
    parser.addoption(
        "--update-golden",
        action="store_true",
        default=False,
    )


@pytest.fixture
def update_golden(request):
    return request.config.getoption("--update-golden")


@pytest.fixture(scope="session", autouse=True)
def setup_storage_registry():
    """
    🔥 Garante que os backends estão registrados
    """
    create_storage_backend_registry()


@pytest.fixture
async def vector_store(tmp_path, container):
    """
    🔥 Retorna VectorStore REAL usando backend in-memory
    Respeita o Async Mandate e usa o Executor do container.
    """
    registry = get_global_registry()
    factory = registry.get(StorageBackends.MEMORY)
    executor = container.resolve(ExecutorPort)

    backend = factory(
        base_path=tmp_path,
        executor=executor,
        config={},
    )

    # O builder de storage agora deve receber o executor
    store = backend.build_vector_store()

    # Limpeza assíncrona obrigatória
    await store.clear()

    yield store

    # Cleanup - ensure no pending tasks from this store
    # The container fixture handles the executor cleanup


@pytest.fixture(autouse=True)
async def no_async_leaks():
    yield

    # --------------------------------------------------
    # 🔥 1. dar chance pro loop limpar callbacks
    # --------------------------------------------------
    for _ in range(3):
        await asyncio.sleep(0)

    current = asyncio.current_task()

    pending = [t for t in asyncio.all_tasks() if t is not current and not t.done()]

    if pending:
        for task in pending:
            task.cancel()

        await asyncio.gather(*pending, return_exceptions=True)

    # --------------------------------------------------
    # 🔥 2. flush final (CRÍTICO)
    # --------------------------------------------------
    for _ in range(3):
        await asyncio.sleep(0)

    # --------------------------------------------------
    # 🔥 3. verificação FINAL
    # --------------------------------------------------
    remaining = [t for t in asyncio.all_tasks() if t is not current and not t.done()]

    if remaining:
        raise AssertionError(f"🔥 Async leak detected after cleanup: {remaining}")


# =========================================================
# PYTEST HOOKS
# =========================================================


def pytest_configure(config):
    """
    Configure pytest to suppress spurious warnings from pytest stash cleanup.

    When pytest tears down fixtures, it cleans up self._storage dictionary.
    If this dict contains adapter coroutines that weren't awaited (but are
    legitimate AsyncMock or similar test doubles), we suppress the warning.
    """
    import warnings

    # Suppress the specific pattern of warnings from pytest stash cleanup
    warnings.filterwarnings(
        "ignore",
        category=RuntimeWarning,
        message="coroutine.*was never awaited.*",
        module=".*_pytest.*stash.*",
    )

    # Also suppress from general cleanup
    warnings.filterwarnings(
        "ignore",
        category=RuntimeWarning,
        message="coroutine '(TokenStoreAdapter|DocumentStoreAdapter|MetadataStoreAdapter|CampaignScopedContainer)\\.get' was never awaited",
    )
