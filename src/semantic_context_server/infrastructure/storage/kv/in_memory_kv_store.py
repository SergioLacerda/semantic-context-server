import asyncio
from typing import Any


class InMemoryKVStore:
    def __init__(self) -> None:
        self._data: dict[str, Any] = {}
        self._lock = asyncio.Lock()

    async def get(self, key: str) -> Any | None:
        async with self._lock:
            return self._data.get(key)

    async def set(self, key: str, value: Any) -> None:
        async with self._lock:
            self._data[key] = value

    async def clear(self) -> None:
        async with self._lock:
            self._data.clear()

    async def delete(self, key: str) -> None:
        async with self._lock:
            self._data.pop(key, None)
