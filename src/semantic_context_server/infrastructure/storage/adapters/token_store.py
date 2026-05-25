from typing import Any

from semantic_context_server.application.ports.executor import ExecutorPort
from semantic_context_server.application.ports.storage import TokenStorePort
from semantic_context_server.infrastructure.storage.base.base_kv_adapter import BaseKVAdapter


class TokenStoreAdapter(BaseKVAdapter, TokenStorePort):
    def __init__(self, kv_store: Any, executor: ExecutorPort) -> None:
        super().__init__(kv_store, executor)

    async def set(self, key: str, value: Any) -> None:
        await super().set(key, value)

    async def get(self, key: str) -> Any:
        return await super().get(key)

    async def clear(self) -> None:
        await super().clear()
