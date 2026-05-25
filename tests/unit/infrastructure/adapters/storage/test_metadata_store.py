import inspect
from unittest.mock import MagicMock

import pytest

from semantic_context_server.infrastructure.storage.adapters.metadata_store import (
    MetadataStoreAdapter,
)
from tests.config.fakes.infrastructure.storage.fake_kv_store import FakeKVStore


@pytest.fixture
def store():
    executor = MagicMock()

    async def mock_run(fn, *args, **kwargs):
        res = fn(*args, **kwargs)
        return await res if inspect.isawaitable(res) else res

    executor.run = mock_run
    return MetadataStoreAdapter(FakeKVStore(), executor)


@pytest.mark.asyncio
async def test_set_and_get_metadata(store):
    await store.set("doc1", {"x": 1})

    result = await store.get("doc1")
    assert result["x"] == 1
