from typing import Any

from semantic_context_server.infrastructure.cache.base.base_cache import BaseCache


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
