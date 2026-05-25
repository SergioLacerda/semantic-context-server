from typing import Any

from semantic_context_server.application.ports.executor import ExecutorPort
from semantic_context_server.application.ports.storage import VectorStorePort


class BaseVectorAdapter(VectorStorePort):
    """
    Base adapter para vector stores.
    """

    def __init__(self, store: Any, executor: ExecutorPort):
        self._store = store
        self._executor = executor

    async def add(
        self,
        doc_id: str,
        vector: list[float],
        metadata: dict[str, Any] | None = None,
    ) -> None:
        # Handle both backends that support metadata and those that don't
        if hasattr(self._store.add, "__code__") and self._store.add.__code__.co_argcount == 4:
            # Backend accepts metadata parameter
            await self._executor.run(self._store.add, doc_id, vector, metadata or {})
        else:
            # Backend only accepts doc_id and vector
            await self._executor.run(self._store.add, doc_id, vector)

    async def get(self, doc_id: str) -> list[float] | None:
        result: list[float] | None = await self._executor.run(self._store.get, doc_id)
        return result

    async def search(self, vector: list[float], k: int = 5) -> list[str]:
        result = await self._executor.run(self._store.search, vector, k)

        if not isinstance(result, list):
            raise TypeError(f"{self._store.__class__.__name__}.search() must return list[str]")

        return result

    async def keys(self) -> list[str]:
        if not hasattr(self._store, "keys"):
            raise NotImplementedError(f"{self._store.__class__.__name__} must implement keys()")

        result: list[str] = await self._executor.run(self._store.keys)
        return result

    async def clear(self) -> None:
        if not hasattr(self._store, "clear"):
            raise NotImplementedError(f"{self._store.__class__.__name__} must implement clear()")

        await self._executor.run(self._store.clear)
