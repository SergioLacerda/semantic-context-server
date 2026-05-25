import pytest

from semantic_context_server.infrastructure.storage.kv.in_memory_kv_store import InMemoryKVStore

# =========================================================
# SYNC STORE FOR TESTING COMPATIBILITY
# =========================================================


class SyncKVStore:
    """Sync KV store para testar compatibilidade com BaseKVAdapter."""

    def __init__(self):
        self._data = {}

    def get(self, key: str):
        return self._data.get(key)

    def set(self, key: str, value):
        self._data[key] = value

    def delete(self, key: str):
        self._data.pop(key, None)

    def clear(self):
        self._data.clear()


# =========================================================
# TESTS
# =========================================================


@pytest.mark.asyncio
@pytest.mark.contract
@pytest.mark.parametrize(
    "store_factory",
    [
        lambda: InMemoryKVStore(),
    ],
)
async def test_kv_contract(store_factory):
    """❌ BASIC CONTRACT - Apenas operações básicas"""
    store = store_factory()

    await store.set("a", 1)
    assert await store.get("a") == 1

    await store.clear()
    assert await store.get("a") is None


@pytest.mark.asyncio
async def test_kv_async_store():
    """✅ ASYNC STORE - Valida async KV store"""
    store = InMemoryKVStore()

    # Set/Get
    await store.set("x", {"nested": "data"})
    assert await store.get("x") == {"nested": "data"}

    # Delete
    await store.delete("x")
    assert await store.get("x") is None

    # Clear
    await store.set("a", 1)
    await store.set("b", 2)
    await store.clear()
    assert await store.get("a") is None
    assert await store.get("b") is None


@pytest.mark.asyncio
async def test_kv_sync_store_compatibility():
    """✅ SYNC STORE COMPATIBILITY - Valida que BaseKVAdapter trabalha com stores síncronos"""
    from unittest.mock import AsyncMock, MagicMock

    from semantic_context_server.infrastructure.storage.base.base_kv_adapter import BaseKVAdapter

    sync_store = SyncKVStore()
    executor = MagicMock()
    executor.run = AsyncMock(side_effect=lambda func, *args, **kwargs: func(*args, **kwargs))

    adapter = BaseKVAdapter(sync_store, executor)

    # Set/Get com sync store
    await adapter.set("key", "value")
    result = await adapter.get("key")
    assert result == "value"

    # Delete com sync store
    await adapter.delete("key")
    result = await adapter.get("key")
    assert result is None

    # Clear com sync store
    await adapter.set("a", 1)
    await adapter.set("b", 2)
    await adapter.clear()
    assert await adapter.get("a") is None


@pytest.mark.asyncio
async def test_kv_multiple_values():
    """✅ MULTIPLE VALUES - Testa múltiplas chaves"""
    store = InMemoryKVStore()

    data = {"k1": "v1", "k2": {"nested": True}, "k3": [1, 2, 3]}

    for k, v in data.items():
        await store.set(k, v)

    for k, v in data.items():
        assert await store.get(k) == v


@pytest.mark.asyncio
async def test_kv_overwrite():
    """✅ OVERWRITE - Testa sobrescrita de valores"""
    store = InMemoryKVStore()

    await store.set("key", "v1")
    assert await store.get("key") == "v1"

    await store.set("key", "v2")
    assert await store.get("key") == "v2"


@pytest.mark.asyncio
async def test_kv_none_values():
    """✅ NONE VALUES - Testa valores None"""
    store = InMemoryKVStore()

    await store.set("key", None)
    assert await store.get("key") is None

    await store.delete("key")
    assert await store.get("key") is None


@pytest.mark.asyncio
async def test_kv_large_values():
    """✅ LARGE VALUES - Testa valores grandes"""
    store = InMemoryKVStore()

    large_data = {"data": "x" * 10000}
    await store.set("large", large_data)

    assert await store.get("large") == large_data
