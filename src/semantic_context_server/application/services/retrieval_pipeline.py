from typing import Any


class RetrievalService:
    def __init__(
        self,
        vector_index: Any,
        planner: Any,
        context_window: Any,
        selector: Any,
        embedding_gateway: Any,
        campaign_id: str,
    ) -> None:
        self.vector_index = vector_index
        self.planner = planner
        self.context_window = context_window
        self.selector = selector
        self.embedding = embedding_gateway
        self.campaign_id = campaign_id

    async def search(self, query: Any, k: int = 4) -> list[Any]:
        # -------------------------
        # 1. EMBEDDING (centralizado)
        # -------------------------
        query_vector = await self.embedding.embed(query)

        if query_vector is None:
            return []

        # -------------------------
        # 2. VECTOR SEARCH (through context window)
        # -------------------------
        docs = await self.context_window.search(query, k)

        # -------------------------
        # 3. POST-PROCESSING
        # -------------------------
        docs = self.selector.select(docs)

        policy = self.context_window.get_policy(query)
        result: list[Any] = self.context_window.apply(docs, policy)

        return result
