from semantic_context_server.infrastructure.cache.base.base_cache import BaseCache
from semantic_context_server.infrastructure.cache.base.base_cache_manager import BaseCacheManager


class EmbeddingCacheManager:
    def __init__(self, base_cache_manager: BaseCacheManager):
        self.base = base_cache_manager

    def get(self, namespace: str) -> BaseCache:
        return self.base.get(f"embedding:{namespace}")

    def invalidate(self, namespace: str) -> None:
        self.base.invalidate(f"embedding:{namespace}")
