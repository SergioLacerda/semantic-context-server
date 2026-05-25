import inspect
from unittest.mock import MagicMock

import pytest

from semantic_context_server.infrastructure.storage.backends.inmemory_backend import (
    InMemoryStorageBackend,
    InMemoryVectorStore,
)


@pytest.fixture
def executor():
    mock = MagicMock()

    async def mock_run(fn, *args, **kwargs):
        # Executa a função e garante o await se for uma corrotina
        res = fn(*args, **kwargs)
        if inspect.isawaitable(res):
            return await res
        return res

    mock.run = mock_run
    return mock


@pytest.mark.asyncio
async def test_inmemory_backend_builds(executor):
    backend = InMemoryStorageBackend(executor)

    vector = backend.build_vector_store()
    doc = backend.build_document_store()

    await vector.add("a", [1, 0])

    assert await vector.get("a") == [1, 0]

    await doc.set("a", {"x": 1})
    result = await doc.get("a")
    assert result is not None, "Storage should return the dict previously set"

    assert result["x"] == 1


def test_vector_store_basic():
    store = InMemoryVectorStore()

    store.add("a", [1, 0])
    store.add("b", [0, 1])

    assert store.get("a") == [1, 0]
    assert set(store.keys()) == {"a", "b"}


def test_vector_store_get_missing():
    store = InMemoryVectorStore()

    assert store.get("missing") is None


def test_vector_store_search():
    store = InMemoryVectorStore()

    store.add("a", [1, 0])
    store.add("b", [0, 1])

    result = store.search([1, 0], limit=1)

    assert result == ["a"]


def test_vector_store_clear():
    store = InMemoryVectorStore()

    store.add("a", [1, 0])
    store.clear()

    assert store.keys() == []


@pytest.mark.asyncio
async def test_inmemory_vector_store_keys_and_clear(executor):
    backend = InMemoryStorageBackend(executor)

    store = backend.build_vector_store()

    await store.add("a", [1, 2, 3])
    await store.add("b", [4, 5, 6])

    keys = await store.keys()
    assert set(keys) == {"a", "b"}

    await store.clear()

    assert await store.keys() == []


@pytest.mark.asyncio
async def test_vector_store_adapter_contract(executor):
    backend = InMemoryStorageBackend(executor)

    store = backend.build_vector_store()

    await store.add("a", [1, 0])

    assert await store.get("a") == [1, 0]
