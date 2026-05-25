from typing import Any

from semantic_context_server.infrastructure.cache.base.async_kv_adapter import AsyncKVAdapter
from semantic_context_server.infrastructure.cache.base.base_cache import BaseCache


class BaseCacheManager:
    """
    Responsável por:
    - Gerenciar instâncias de cache por namespace
    - Garantir isolamento multi-tenant
    - Centralizar construção de caches

    NÃO contém lógica de domínio.
    """

    def __init__(self, kv_provider: Any, ttl: int | None = None) -> None:
        """
        kv_provider:
            Deve fornecer KV store por namespace
            Ex:
                kv_provider.get(namespace)
        """
        self.kv_provider = kv_provider
        self.ttl = ttl

        self._instances: dict[str, BaseCache] = {}

    # ---------------------------------------------------------
    # 🔧 FACTORY
    # ---------------------------------------------------------
    def _build_cache(self, namespace: str) -> BaseCache:
        kv = self.kv_provider.get(namespace)

        return BaseCache(
            kv_store=AsyncKVAdapter(kv),
            ttl=self.ttl,
        )

    # ---------------------------------------------------------
    # 📦 PUBLIC API
    # ---------------------------------------------------------
    def get(self, namespace: str) -> BaseCache:
        if namespace not in self._instances:
            self._instances[namespace] = self._build_cache(namespace)

        return self._instances[namespace]

    def invalidate(self, namespace: str) -> None:
        self._instances.pop(namespace, None)

    def clear_all(self) -> None:
        self._instances.clear()
