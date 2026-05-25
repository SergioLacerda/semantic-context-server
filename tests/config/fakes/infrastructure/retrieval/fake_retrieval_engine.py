class FakeRetrievalEngine:
    def __init__(self, data: dict[str, list[dict]] | None = None):
        """
        data:
            {
                "campaign_id": [{"text": "..."}]
            }
        """
        self.data = data or {}
        self.calls: list[dict] = []

    # ---------------------------------------------------------

    async def search(self, query: str, *, campaign_id: str | None = None, k: int = 5):
        self.calls.append(
            {
                "query": query,
                "campaign_id": campaign_id,
                "k": k,
            }
        )

        if campaign_id and campaign_id in self.data:
            docs = self.data[campaign_id]
        else:
            docs = [d for v in self.data.values() for d in v]

        # simples ranking determinístico
        query_lower = (query or "").lower()

        scored = []
        for doc in docs:
            text = doc.get("text", "")
            score = 1 if query_lower in text.lower() else 0
            scored.append((doc, score))

        scored.sort(key=lambda x: x[1], reverse=True)

        return [doc for doc, _ in scored[:k]]
