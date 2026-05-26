from __future__ import annotations

from typing import Any

from packages.features.semantic_cache.base_cache import BaseCache


class SemanticCache(BaseCache):
    def _make_key(self, *parts: Any) -> str:
        return "::".join(str(part) for part in parts)

    async def get(self, *parts: Any) -> Any | None:
        key = self._make_key(*parts)
        return await super().get(key)

    async def set(self, *parts: Any) -> None:
        if len(parts) < 2:
            raise ValueError("SemanticCache.set requires at least a key and a value")
        *key_parts, value = parts
        key = self._make_key(*key_parts)
        await super().set(key, value)

    async def search(self, *parts: Any) -> Any:
        return await self.get(*parts)

    async def store(self, *parts: Any) -> None:
        await self.set(*parts)


class EmbeddingCache(BaseCache):
    def __init__(self, kv_store: Any, client: Any, ttl: int | None = None) -> None:
        super().__init__(kv_store, ttl)
        self.client = client

    async def get_or_create(self, text: str) -> Any:
        cached = await self.get(text)
        if cached:
            return cached
        embedding = await self.client.embed(text)
        await self.set(text, embedding)
        return embedding


class ResponseCache(BaseCache):
    pass
