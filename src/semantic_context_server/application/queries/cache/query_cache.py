import asyncio
import time
from collections import OrderedDict
from typing import Any


class QueryCache:
    """
    Async-safe TTL + LRU cache for query results.

    Features:
    - TTL expiration
    - LRU eviction
    - async-safe access
    """

    def __init__(self, ttl: int = 60, max_size: int = 256):
        self.ttl = ttl
        self.max_size = max_size

        self._cache: OrderedDict[str, tuple[Any, float]] = OrderedDict()
        self._lock = asyncio.Lock()

    async def invalidate_prefix(self, prefix: str) -> None:
        async with self._lock:
            to_delete = [key for key in self._cache if key.startswith(prefix)]

            for key in to_delete:
                self._cache.pop(key, None)

    # ==========================================================
    # PUBLIC API
    # ==========================================================

    async def get(self, key: str) -> Any | None:
        now = time.time()

        async with self._lock:
            entry = self._cache.get(key)

            if not entry:
                return None

            value, ts = entry

            if now - ts > self.ttl:
                self._cache.pop(key, None)
                return None

            self._cache.move_to_end(key)

            return value

    async def set(self, key: str, value: Any) -> None:
        now = time.time()

        async with self._lock:
            self._cache[key] = (value, now)
            self._cache.move_to_end(key)

            while len(self._cache) > self.max_size:
                self._cache.popitem(last=False)

    async def delete(self, key: str) -> None:
        async with self._lock:
            self._cache.pop(key, None)

    async def clear(self) -> None:
        async with self._lock:
            self._cache.clear()

    # ==========================================================
    # UTILITIES
    # ==========================================================

    async def stats(self) -> dict:
        async with self._lock:
            return {
                "size": len(self._cache),
                "max_size": self.max_size,
                "ttl": self.ttl,
            }
