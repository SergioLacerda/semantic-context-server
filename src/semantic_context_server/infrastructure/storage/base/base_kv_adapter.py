import inspect
from typing import Any

from semantic_context_server.application.ports.executor import ExecutorPort
from semantic_context_server.application.ports.storage import KeyValueStorePort


class BaseKVAdapter(KeyValueStorePort):
    """
    Base adapter para KV-based stores.

    ✔ Compatível com stores síncronos e assíncronos
    ✔ Métodos síncronos são executados via executor para não bloquear event loop
    """

    def __init__(self, store: Any, executor: ExecutorPort):
        self._store = store
        self._executor = executor

    async def get(self, key: str) -> Any:
        result = self._store.get(key)
        # ✔ Handle both sync and async stores
        return await result if inspect.isawaitable(result) else result

    async def set(self, key: str, value: Any) -> Any:
        result = self._store.set(key, value)
        return await result if inspect.isawaitable(result) else result

    async def delete(self, key: str) -> Any:
        result = self._store.delete(key)
        return await result if inspect.isawaitable(result) else result

    async def clear(self) -> Any:
        result = self._store.clear()
        return await result if inspect.isawaitable(result) else result
