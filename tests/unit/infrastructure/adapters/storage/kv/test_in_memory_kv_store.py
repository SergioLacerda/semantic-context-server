import pytest

from semantic_context_server.infrastructure.storage.kv.in_memory_kv_store import (
    InMemoryKVStore,
)


@pytest.mark.asyncio
async def test_set_and_get():
    store = InMemoryKVStore()

    await store.set("a", 1)

    assert await store.get("a") == 1


@pytest.mark.asyncio
async def test_get_missing():
    store = InMemoryKVStore()

    assert await store.get("missing") is None


@pytest.mark.asyncio
async def test_clear():
    store = InMemoryKVStore()

    await store.set("a", 1)
    await store.clear()

    assert await store.get("a") is None
