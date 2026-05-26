from __future__ import annotations

import contextlib
import time
from typing import Any


class AsyncKVAdapter:
    def __init__(self, kv: Any) -> None:
        self.kv = kv

    async def get(self, key: str) -> Any:
        return await self.kv.get(key)

    async def set(self, key: str, value: Any) -> Any:
        return await self.kv.set(key, value)

    async def delete(self, key: str) -> Any:
        if hasattr(self.kv, "delete"):
            return await self.kv.delete(key)

    async def clear(self) -> Any:
        if hasattr(self.kv, "clear"):
            return await self.kv.clear()

    async def keys(self) -> Any:
        return await self.kv.keys()


class BaseCache:
    def __init__(self, kv_store: Any, ttl: int | None = None) -> None:
        self.kv = kv_store
        self.ttl = ttl

    def _now(self) -> float:
        return time.time()

    def _is_expired(self, ts: float, ttl: int | None) -> bool:
        if ttl is None:
            return False
        return (self._now() - ts) > ttl

    def _safe_unpack(self, data: Any) -> tuple[Any, Any, Any]:
        try:
            value, ts, ttl = data
            return value, ts, ttl
        except Exception:
            return None, None, None

    async def get(self, key: str) -> Any | None:
        data = await self.kv.get(key)
        if not data:
            return None
        value, ts, ttl = self._safe_unpack(data)
        if ts is None:
            return None
        if self._is_expired(ts, ttl):
            with contextlib.suppress(Exception):
                await self.kv.delete(key)
            return None
        return value

    async def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        effective_ttl = ttl if ttl is not None else self.ttl
        payload = (value, self._now(), effective_ttl)
        await self.kv.set(key, payload)

    async def delete(self, key: str) -> None:
        with contextlib.suppress(Exception):
            await self.kv.delete(key)

    async def invalidate(self, key: str) -> None:
        await self.delete(key)

    async def clear(self) -> None:
        if hasattr(self.kv, "clear"):
            with contextlib.suppress(Exception):
                await self.kv.clear()

    async def exists(self, key: str) -> bool:
        data = await self.kv.get(key)
        if not data:
            return False
        _, ts, ttl = self._safe_unpack(data)
        if ts is None:
            return False
        return not self._is_expired(ts, ttl)
