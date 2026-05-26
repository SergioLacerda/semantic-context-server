from packages.features.semantic_cache.base_cache import BaseCache
from packages.features.semantic_cache.cache_manager import (
    BaseCacheManager,
)
from tests.config.fakes.infrastructure.storage.fake_kv_store import FakeKVStore


class FakeKVProvider:
    def __init__(self):
        self.instances = {}
        self.calls = []

    def get(self, namespace: str):
        self.calls.append(namespace)
        return self.instances.setdefault(namespace, FakeKVStore())


def test_get_returns_cached_instance_per_namespace():
    manager = BaseCacheManager(kv_provider=FakeKVProvider(), ttl=30)

    cache_a1 = manager.get("campaign:a")
    cache_a2 = manager.get("campaign:a")

    assert cache_a1 is cache_a2


def test_get_creates_distinct_instances_per_namespace():
    manager = BaseCacheManager(kv_provider=FakeKVProvider(), ttl=30)

    cache_a = manager.get("campaign:a")
    cache_b = manager.get("campaign:b")

    assert cache_a is not cache_b
    assert isinstance(cache_a, BaseCache)
    assert isinstance(cache_b, BaseCache)


def test_invalidate_removes_cached_namespace():
    manager = BaseCacheManager(kv_provider=FakeKVProvider(), ttl=30)

    cache_a1 = manager.get("campaign:a")
    manager.invalidate("campaign:a")
    cache_a2 = manager.get("campaign:a")

    assert cache_a1 is not cache_a2


def test_clear_all_removes_all_cached_instances():
    manager = BaseCacheManager(kv_provider=FakeKVProvider(), ttl=30)

    manager.get("campaign:a")
    manager.get("campaign:b")
    manager.clear_all()

    assert manager._instances == {}
