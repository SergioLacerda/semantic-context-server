from typing import Any, cast

from semantic_context_server.application.ports.executor import ExecutorPort
from semantic_context_server.application.ports.storage import VectorStorePort


class ChromaVectorAdapter(VectorStorePort):
    """
    Exemplo de conformidade com Sync Adapters rule:
    O Port é async, mas a lib (Chroma) é sync.
    """

    def __init__(self, client: Any, executor: ExecutorPort) -> None:
        self.client = client
        self.executor = executor
        self._collection = client.get_or_create_collection("narrative")

    async def add(
        self,
        doc_id: str,
        vector: list[float],
        metadata: dict[str, Any] | None = None,
    ) -> None:
        # Delega para thread pool para não bloquear o Event Loop
        meta = metadata or {}
        await self.executor.run(
            lambda: self._collection.add(ids=[doc_id], embeddings=[vector], metadatas=[meta])
        )

    async def search(self, vector: list[float], limit: int = 5) -> list[str]:
        results = await self.executor.run(
            lambda: self._collection.query(query_embeddings=[vector], n_results=limit)
        )
        return cast(list[str], results.get("ids", [[]])[0])

    async def get(self, doc_id: str) -> list[float] | None:
        res = await self.executor.run(lambda: self._collection.get(ids=[doc_id]))
        if not res["ids"]:
            return None
        if res.get("embeddings"):
            return cast(list[float], res["embeddings"][0])
        return None

    async def clear(self) -> None:
        # Operação perigosa, sempre via executor
        await self.executor.run(lambda: self.client.delete_collection("narrative"))

    async def keys(self) -> list[str]:
        res = await self.executor.run(lambda: self._collection.get())
        return cast(list[str], res.get("ids", []))
