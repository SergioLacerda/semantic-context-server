from __future__ import annotations

from typing import Any

from packages.core.shared_kernel import normalize_text, stable_sha256
from packages.features.semantic_cache.contracts import SemanticCacheContract


class SemanticCacheService(SemanticCacheContract):
    """Package-level semantic cache using normalized prompt keys."""

    def __init__(self) -> None:
        self._store: dict[str, Any] = {}

    def _key(self, prompt: str) -> str:
        return stable_sha256(normalize_text(prompt))

    async def get(self, prompt: str) -> Any | None:
        return self._store.get(self._key(prompt))

    async def set(self, prompt: str, value: Any) -> None:
        self._store[self._key(prompt)] = value

    async def invalidate(self, prompt: str) -> None:
        self._store.pop(self._key(prompt), None)

    async def clear(self) -> None:
        self._store.clear()


class LegacySemanticCacheAdapter:
    """Compatibility adapter for legacy semantic cache call patterns."""

    def __init__(self) -> None:
        self._store: dict[str, Any] = {}

    def _part(self, value: Any) -> str:
        if isinstance(value, str):
            return normalize_text(value)
        return str(value)

    def _key(self, *parts: Any) -> str:
        raw = "::".join(self._part(p) for p in parts)
        return stable_sha256(raw)

    async def get(self, *parts: Any) -> Any | None:
        return self._store.get(self._key(*parts))

    async def set(self, *parts: Any) -> None:
        if len(parts) < 2:
            raise ValueError("LegacySemanticCacheAdapter.set requires at least key parts and value")
        *key_parts, value = parts
        self._store[self._key(*key_parts)] = value

    async def search(self, *parts: Any) -> Any:
        return await self.get(*parts)

    async def store(self, *parts: Any) -> None:
        await self.set(*parts)
