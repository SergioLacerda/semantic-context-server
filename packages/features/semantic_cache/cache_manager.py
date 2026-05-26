from __future__ import annotations

from typing import Any

from packages.features.semantic_cache.base_cache import AsyncKVAdapter, BaseCache
from packages.features.semantic_cache.implementations import SemanticCache


class BaseCacheManager:
    def __init__(self, kv_provider: Any, ttl: int | None = None) -> None:
        self.kv_provider = kv_provider
        self.ttl = ttl
        self._instances: dict[str, BaseCache] = {}

    def _build_cache(self, namespace: str) -> BaseCache:
        kv = self.kv_provider.get(namespace)
        return BaseCache(kv_store=AsyncKVAdapter(kv), ttl=self.ttl)

    def get(self, namespace: str) -> BaseCache:
        if namespace not in self._instances:
            self._instances[namespace] = self._build_cache(namespace)
        return self._instances[namespace]

    def invalidate(self, namespace: str) -> None:
        self._instances.pop(namespace, None)

    def clear_all(self) -> None:
        self._instances.clear()


class SemanticCacheManager:
    def __init__(self, base_cache_manager: Any) -> None:
        self.base = base_cache_manager
        self._instances: dict[str, SemanticCache] = {}

    def get(self, namespace: str) -> SemanticCache:
        if namespace not in self._instances:
            kv = self.base.kv_provider.get(f"semantic:{namespace}")
            self._instances[namespace] = SemanticCache(AsyncKVAdapter(kv), ttl=self.base.ttl)
        return self._instances[namespace]

    def invalidate(self, namespace: str) -> None:
        self._instances.pop(namespace, None)


class EmbeddingCacheManager:
    def __init__(self, base_cache_manager: BaseCacheManager) -> None:
        self.base = base_cache_manager

    def get(self, namespace: str) -> BaseCache:
        return self.base.get(f"embedding:{namespace}")

    def invalidate(self, namespace: str) -> None:
        self.base.invalidate(f"embedding:{namespace}")


class ResponseCacheManager:
    def __init__(self, base_cache_manager: Any) -> None:
        self.base = base_cache_manager

    def get(self, namespace: str) -> Any:
        return self.base.get(f"response:{namespace}")

    def invalidate(self, namespace: str) -> None:
        self.base.invalidate(f"response:{namespace}")
