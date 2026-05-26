import pytest

from packages.features.semantic_cache.base_cache import (
    AsyncKVAdapter,
    BaseCache,
)
from tests.config.fakes.infrastructure.storage.fake_kv_store import FakeKVStore


class FrozenTimeCache(BaseCache):
    def __init__(self, kv_store, ttl=None, now=100.0):
        super().__init__(kv_store, ttl=ttl)
        self.now = now

    def _now(self) -> float:
        return self.now


@pytest.mark.asyncio
async def test_set_and_get_returns_value():
    cache = BaseCache(kv_store=AsyncKVAdapter(FakeKVStore()))

    await cache.set("a", 123)

    assert await cache.get("a") == 123


@pytest.mark.asyncio
async def test_get_returns_none_for_missing_key():
    cache = BaseCache(kv_store=AsyncKVAdapter(FakeKVStore()))

    assert await cache.get("missing") is None


@pytest.mark.asyncio
async def test_get_deletes_expired_entries():
    kv = AsyncKVAdapter(FakeKVStore())
    cache = FrozenTimeCache(kv_store=kv, ttl=10, now=100.0)

    await cache.set("a", 123)
    cache.now = 111.0

    assert await cache.get("a") is None
    assert await kv.get("a") is None


@pytest.mark.asyncio
async def test_get_returns_none_for_invalid_payload():
    kv = AsyncKVAdapter(FakeKVStore())
    cache = BaseCache(kv_store=kv)

    await kv.set("broken", {"unexpected": True})

    assert await cache.get("broken") is None


@pytest.mark.asyncio
async def test_set_uses_default_ttl_when_not_overridden():
    kv = AsyncKVAdapter(FakeKVStore())
    cache = FrozenTimeCache(kv_store=kv, ttl=30, now=100.0)

    await cache.set("a", 1)

    assert await kv.get("a") == (1, 100.0, 30)


@pytest.mark.asyncio
async def test_set_allows_per_call_ttl_override():
    kv = AsyncKVAdapter(FakeKVStore())
    cache = FrozenTimeCache(kv_store=kv, ttl=30, now=100.0)

    await cache.set("a", 1, ttl=5)

    assert await kv.get("a") == (1, 100.0, 5)


@pytest.mark.asyncio
async def test_delete_removes_key():
    cache = BaseCache(kv_store=AsyncKVAdapter(FakeKVStore()))

    await cache.set("a", 1)
    await cache.delete("a")

    assert await cache.get("a") is None


@pytest.mark.asyncio
async def test_invalidate_aliases_delete():
    cache = BaseCache(kv_store=AsyncKVAdapter(FakeKVStore()))

    await cache.set("a", 1)
    await cache.invalidate("a")

    assert await cache.get("a") is None


@pytest.mark.asyncio
async def test_clear_removes_all_entries():
    cache = BaseCache(kv_store=AsyncKVAdapter(FakeKVStore()))

    await cache.set("a", 1)
    await cache.set("b", 2)
    await cache.clear()

    assert await cache.get("a") is None
    assert await cache.get("b") is None


@pytest.mark.asyncio
async def test_exists_is_true_for_valid_key():
    cache = BaseCache(kv_store=AsyncKVAdapter(FakeKVStore()))

    await cache.set("a", 1)

    assert await cache.exists("a") is True


@pytest.mark.asyncio
async def test_exists_is_false_for_expired_key():
    kv = AsyncKVAdapter(FakeKVStore())
    cache = FrozenTimeCache(kv_store=kv, ttl=10, now=100.0)

    await cache.set("a", 1)
    cache.now = 111.0

    assert await cache.exists("a") is False
