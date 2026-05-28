from __future__ import annotations

import time
from collections import OrderedDict
from typing import Any


class RuntimeScopeManager:
    """TTL + LRU runtime cache generalized to world/scope IDs."""

    def __init__(self, builder: Any, max_size: int = 100, ttl_seconds: int = 3600) -> None:
        self.builder = builder
        self.cache: OrderedDict[str, tuple[Any, float]] = OrderedDict()
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds

    @staticmethod
    def _key(world_id: str, scope_id: str) -> str:
        return f"{world_id}::{scope_id}"

    async def get(self, world_id: str, scope_id: str) -> Any:
        now = time.time()
        key = self._key(world_id, scope_id)

        if key in self.cache:
            runtime, _ = self.cache[key]
            self.cache.move_to_end(key)
            self.cache[key] = (runtime, now)
            return runtime

        runtime = await self.builder.build_scope_runtime(world_id, scope_id)
        self.cache[key] = (runtime, now)
        await self._evict(now)
        return runtime

    async def _evict(self, now: float) -> None:
        expired = [k for k, (_, ts) in self.cache.items() if now - ts > self.ttl_seconds]
        for key in expired:
            runtime, _ = self.cache.pop(key)
            if hasattr(runtime, "shutdown"):
                await runtime.shutdown()

        while len(self.cache) > self.max_size:
            _, (runtime, _) = self.cache.popitem(last=False)
            if hasattr(runtime, "shutdown"):
                await runtime.shutdown()

    async def clear(self, world_id: str, scope_id: str) -> None:
        key = self._key(world_id, scope_id)
        if key in self.cache:
            runtime, _ = self.cache.pop(key)
            if hasattr(runtime, "shutdown"):
                await runtime.shutdown()

    async def shutdown(self) -> None:
        for runtime, _ in self.cache.values():
            if hasattr(runtime, "shutdown"):
                await runtime.shutdown()
        self.cache.clear()
