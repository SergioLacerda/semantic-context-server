from __future__ import annotations

from typing import Any

from packages.features.embedding_gateway.contracts import EmbeddingGatewayContract
from packages.features.vector_index.contracts import VectorIndexContract, VectorStoreContract


class VectorIndexService(VectorIndexContract):
    """Black-box vector index service that depends only on embedding contracts."""

    def __init__(self, embedding_gateway: EmbeddingGatewayContract, store: VectorStoreContract) -> None:
        self._embedding_gateway = embedding_gateway
        self._store = store

    async def search_by_text(self, query: str, k: int = 4) -> list[dict[str, Any]]:
        vector = await self._embedding_gateway.embed(query)
        if vector is None:
            return []
        return await self._store.search(vector=vector, k=k)
