import pytest

from tests.config.fakes.infrastructure.storage.failure_modes.fake_failing_storage import (
    FailingStorageConfig,
)
from tests.config.fakes.infrastructure.storage.fake_storage_config import FakeStorageConfig


@pytest.mark.integration
@pytest.mark.slow
@pytest.mark.asyncio
async def test_storage_failure(container_factory):
    container = container_factory(storage_config=FailingStorageConfig())
    campaign = await container.campaigns.get("c1")

    store = campaign.storage.build_document_store()

    with pytest.raises(RuntimeError):
        await store.set("x", {"v": 1})


@pytest.mark.integration
@pytest.mark.slow
@pytest.mark.parametrize(
    "storage_type",
    ["inmemory", "json", "failing"],
)
@pytest.mark.asyncio
async def test_storage_behaviour(container_factory, tmp_path, storage_type):
    config = FakeStorageConfig(namespace=storage_type, base_path=str(tmp_path))
    container = container_factory(storage_config=config)
    campaign = await container.campaigns.get("c1")

    store = campaign.storage.build_document_store()

    if storage_type == "failing":
        with pytest.raises(RuntimeError):
            await store.set("a", {"v": 1})
    else:
        await store.set("a", {"v": 1})
        result = await store.get("a")

        assert result == {"v": 1}
