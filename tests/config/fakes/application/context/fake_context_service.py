class FakeContextService:
    def __init__(
        self,
        data: dict[str, list[str]] | None = None,
        graph=None,
    ):
        """
        data:
            {
                "c1": ["you found a sword", "there is a chest"],
                "c2": ["you found a key"]
            }
        """
        self.data = data or {}
        self.graph = graph

        self.calls: list[dict] = []

    # ---------------------------------------------------------
    # MAIN API
    # ---------------------------------------------------------

    async def search(
        self,
        query: str,
        k: int = 4,
        intent: str | None = None,
        campaign_id: str | None = None,
    ) -> list[str]:
        self.calls.append({"query": query, "k": k, "intent": intent, "campaign_id": campaign_id})

        if not query:
            return []

        query_lower = query.lower()
        docs = self._collect_docs(campaign_id)
        docs = await self._expand_with_graph(docs, query_lower)
        return self._score_and_rank(docs, query_lower, k)

    def _collect_docs(self, campaign_id: str | None) -> list[str]:
        if campaign_id and campaign_id in self.data:
            return list(self.data[campaign_id])
        return [doc for docs in self.data.values() for doc in docs]

    async def _expand_with_graph(self, docs: list[str], query_lower: str) -> list[str]:
        if self.graph and hasattr(self.graph, "related"):
            try:
                related = await self.graph.related(query_lower)
                docs = docs + [f"related: {r}" for r in related]
            except Exception:
                pass
        return docs

    def _score_and_rank(self, docs: list[str], query_lower: str, k: int) -> list[str]:
        def score(text: str) -> int:
            t = text.lower()
            return (2 if query_lower in t else 0) + sum(
                1 for tok in query_lower.split() if tok in t
            )

        scored = sorted(docs, key=score, reverse=True)
        return scored[:k]
