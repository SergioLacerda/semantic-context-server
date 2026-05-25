from typing import Any

from semantic_context_server.infrastructure.cache.base.async_kv_adapter import AsyncKVAdapter
from semantic_context_server.infrastructure.cache.implementations.semantic_cache import (
    SemanticCache,
)


class SemanticCacheManager:
    def __init__(self, base_cache_manager: Any) -> None:
        self.base = base_cache_manager
        self._instances: dict[str, SemanticCache] = {}

    def get(self, namespace: str) -> SemanticCache:
        if namespace not in self._instances:
            kv = self.base.kv_provider.get(f"semantic:{namespace}")
            self._instances[namespace] = SemanticCache(
                AsyncKVAdapter(kv),
                ttl=self.base.ttl,
            )

        return self._instances[namespace]

    def invalidate(self, namespace: str) -> None:
        self._instances.pop(namespace, None)
