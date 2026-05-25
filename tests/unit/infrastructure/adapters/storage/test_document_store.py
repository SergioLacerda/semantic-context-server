import inspect
from unittest.mock import MagicMock

import pytest

from semantic_context_server.infrastructure.storage.adapters.document_store import (
    DocumentStoreAdapter,
)
from tests.config.fakes.infrastructure.storage.fake_kv_store import FakeKVStore


@pytest.fixture
def store():
    executor = MagicMock()

    async def mock_run(fn, *args, **kwargs):
        res = fn(*args, **kwargs)
        return await res if inspect.isawaitable(res) else res

    executor.run = mock_run
    return DocumentStoreAdapter(FakeKVStore(), executor)


@pytest.mark.asyncio
async def test_set_and_get(store):
    await store.set("doc1", {"a": 1})

    result = await store.get("doc1")
    assert result["a"] == 1


@pytest.mark.asyncio
async def test_set_invalid_doc_id(store):
    with pytest.raises(ValueError):
        await store.set("", {"a": 1})


@pytest.mark.asyncio
async def test_set_invalid_document(store):
    with pytest.raises(TypeError):
        await store.set("doc1", "invalid")


@pytest.mark.asyncio
async def test_get_empty_id(store):
    assert await store.get("") is None


@pytest.mark.asyncio
async def test_clear():
    kv = FakeKVStore()
    executor = MagicMock()

    async def mock_run(fn, *args, **kwargs):
        res = fn(*args, **kwargs)
        return await res if inspect.isawaitable(res) else res

    executor.run = mock_run
    store = DocumentStoreAdapter(kv, executor)

    await store.set("doc1", {"a": 1})
    await store.clear()

    assert await store.get("doc1") is None


@pytest.mark.asyncio
async def test_clear_without_clear_method_does_not_crash():
    class FakeStore:
        def set(self, k, v):
            pass

        def get(self, k):
            return None

        def clear(self):
            pass

    executor = MagicMock()

    async def mock_run(fn, *args, **kwargs):
        res = fn(*args, **kwargs)
        return await res if inspect.isawaitable(res) else res

    executor.run = mock_run
    store = DocumentStoreAdapter(FakeStore(), executor)

    await store.clear()

    assert True
