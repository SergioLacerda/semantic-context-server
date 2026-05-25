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
