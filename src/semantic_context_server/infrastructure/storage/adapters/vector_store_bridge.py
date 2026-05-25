from typing import Any

from semantic_context_server.application.ports.storage import VectorStorePort


class VectorStoreBridge:
    def __init__(self, store: VectorStorePort) -> None:
        self.store = store

    async def add(
        self,
        doc_id: str,
        vector: list[float],
        metadata: dict[str, Any] | None = None,
    ) -> None:
        await self.store.add(doc_id, vector, metadata or {})

    async def get(self, doc_id: str) -> list[float] | None:
        return await self.store.get(doc_id)

    async def search(self, query_vector: list[float], k: int) -> list[str]:
        results = await self.store.search(query_vector, k)
        return results

    async def keys(self) -> list[str]:
        return await self.store.keys()
