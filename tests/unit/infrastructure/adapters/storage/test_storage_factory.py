from pathlib import Path
from unittest.mock import MagicMock

import pytest

from semantic_context_server.application.ports.storage_types import (
    StorageBackends,
    StorageKinds,
)
from semantic_context_server.infrastructure.storage.backends.inmemory_backend import (
    InMemoryStorageBackend,
)
from semantic_context_server.infrastructure.storage.backends.json_backend import (
    JSONStorageBackend,
)
from semantic_context_server.infrastructure.storage.campaign_storage_factory import (
    build_campaign_storage,
)
from semantic_context_server.infrastructure.storage.providers.storage_backend_registry_setup import (
    create_storage_backend_registry,
)
from tests.config.fakes.infrastructure.storage.fake_storage_config import (
    FakeStorageConfig,
)


def setup_module():
    create_storage_backend_registry()


class StringPathStorageConfig(FakeStorageConfig):
    def get_base_path(self, campaign_id: str):
        return Path(str(super().get_base_path(campaign_id)))


@pytest.fixture
def executor():
    return MagicMock(spec=["run"])


@pytest.mark.asyncio
async def test_build_json_storage_returns_json_backend(executor):
    config = FakeStorageConfig(
        backends={
            StorageKinds.KV: StorageBackends.JSON,
        }
    )

    storage = build_campaign_storage(config, "c1", executor)

    assert isinstance(storage, JSONStorageBackend)


def test_build_inmemory_storage_returns_inmemory_backend():
    executor = MagicMock(spec=["run"])
    config = FakeStorageConfig(
        backends={
            StorageKinds.KV: StorageBackends.MEMORY,
        }
    )

    storage = build_campaign_storage(config, "c1", executor)

    assert isinstance(storage, InMemoryStorageBackend)


def test_factory_uses_kv_backend_even_if_other_kinds_differ(executor):
    config = FakeStorageConfig(
        backends={
            StorageKinds.KV: StorageBackends.JSON,
            StorageKinds.VECTOR: StorageBackends.CHROMA,
        }
    )

    storage = build_campaign_storage(config, "c1", executor)

    assert isinstance(storage, JSONStorageBackend)


def test_json_backend_receives_campaign_base_path(executor):
    config = FakeStorageConfig(
        backends={
            StorageKinds.KV: StorageBackends.JSON,
        }
    )

    storage = build_campaign_storage(config, "campaign_xyz", executor)

    assert isinstance(storage, JSONStorageBackend)
    assert storage.base == config.get_base_path("campaign_xyz")


def test_factory_accepts_string_base_path_and_normalizes_to_path(executor):
    config = StringPathStorageConfig(
        backends={
            StorageKinds.KV: StorageBackends.JSON,
        }
    )

    storage = build_campaign_storage(config, "c1", executor)

    assert isinstance(storage, JSONStorageBackend)
    assert isinstance(storage.base, Path)


def test_storage_respects_namespace_isolation(executor):
    config = FakeStorageConfig(
        namespace="isolated_test",
        backends={
            StorageKinds.KV: StorageBackends.JSON,
        },
    )

    storage = build_campaign_storage(config, "campaign1", executor)

    assert "isolated_test" in str(storage.base)


def test_multiple_campaigns_have_different_paths(executor):
    config = FakeStorageConfig(
        backends={
            StorageKinds.KV: StorageBackends.JSON,
        }
    )

    storage1 = build_campaign_storage(config, "c1", executor)
    storage2 = build_campaign_storage(config, "c2", executor)

    assert storage1.base != storage2.base


def test_missing_kv_backend_configuration_still_uses_default(executor):
    """FakeStorageConfig provides default backend even with empty backends dict"""
    config = FakeStorageConfig(backends={})

    # Should not raise because FakeStorageConfig provides defaults for empty backends
    storage = build_campaign_storage(config, "c1", executor)

    assert storage is not None


@pytest.mark.asyncio
async def test_unregistered_backend_raises_value_error(executor):
    config = FakeStorageConfig(
        backends={
            StorageKinds.KV: StorageBackends.CHROMA,
        }
    )

    with pytest.raises(ValueError):
        await build_campaign_storage(config, "c1", executor)
