from semantic_context_server.application.ports.vector_writer_port import VectorWriterPort


class FakeVectorMemory(VectorWriterPort):
    def __init__(self):
        self._store: dict[str, list[dict]] = {}
        self.calls: list[dict] = []

    # ---------------------------------------------------------
    # REQUIRED BY PORT 🔥
    # ---------------------------------------------------------

    async def store_event(
        self,
        *,
        campaign_id: str,
        texts: list[str],
        metadata: dict | None = None,
    ):
        self.calls.append(
            {
                "op": "store_event",
                "campaign_id": campaign_id,
                "texts": texts,
            }
        )

        if campaign_id not in self._store:
            self._store[campaign_id] = []

        for text in texts:
            self._store[campaign_id].append(
                {
                    "text": text,
                    "metadata": metadata or {},
                }
            )

    # ---------------------------------------------------------
    # SEARCH (provavelmente também no port)
    # ---------------------------------------------------------

    async def search(
        self,
        *,
        campaign_id: str,
        query: str,
        k: int = 5,
    ) -> list[dict]:
        self.calls.append(
            {
                "op": "search",
                "campaign_id": campaign_id,
                "query": query,
            }
        )

        items = self._store.get(campaign_id, [])

        query_lower = (query or "").lower()

        results = []

        for item in items:
            if query_lower in item["text"].lower():
                results.append(item)

        return results[:k]
