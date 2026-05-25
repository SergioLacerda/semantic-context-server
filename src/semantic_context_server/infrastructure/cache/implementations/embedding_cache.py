from typing import Any

from semantic_context_server.infrastructure.cache.base.base_cache import BaseCache


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
