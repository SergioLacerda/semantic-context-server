import inspect
from unittest.mock import MagicMock

import pytest

from semantic_context_server.infrastructure.storage.adapters.vector_store import VectorStoreAdapter
from semantic_context_server.infrastructure.storage.backends.inmemory_backend import (
    InMemoryVectorStore,
)

# ---------------------------------------------------------
# DUMMY
# ---------------------------------------------------------


class DummyBackend:
    def __init__(self):
        self.data = {}
        self.last_search = None

    def add(self, k, v, metadata=None):
        self.data[k] = v

    def get(self, k):
        return self.data.get(k)

    def search(self, q, k):
        self.last_search = (q, k)
        return list(self.data.keys())[:k]

    def keys(self):
        return list(self.data.keys())


@pytest.fixture
def backend():
    return DummyBackend()


@pytest.fixture
def store(backend):
    executor = MagicMock()

    async def mock_run(fn, *args, **kwargs):
        res = fn(*args, **kwargs)
        return await res if inspect.isawaitable(res) else res

    executor.run = mock_run
    return VectorStoreAdapter(backend, executor)


@pytest.mark.asyncio
async def test_vector_adapter_basic(store):
    await store.add("doc1", [1, 0], {"type": "test"})

    assert await store.get("doc1") == [1, 0]
    assert await store.keys() == ["doc1"]
    assert await store.search([1, 0], 1) == ["doc1"]


@pytest.mark.asyncio
async def test_search_calls_backend(backend, store):
    await store.add("doc1", [1, 0], {})

    await store.search([1, 0], 2)

    assert backend.last_search == ([1, 0], 2)


@pytest.mark.asyncio
async def test_vector_store_adapter_keys():
    store = InMemoryVectorStore()
    executor = MagicMock()

    async def mock_run(fn, *args, **kwargs):
        res = fn(*args, **kwargs)
        return await res if inspect.isawaitable(res) else res

    executor.run = mock_run
    adapter = VectorStoreAdapter(store, executor)

    await adapter.add("a", [1, 0], {"test": True})

    assert await adapter.keys() == ["a"]
