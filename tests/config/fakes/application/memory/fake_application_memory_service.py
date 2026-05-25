from semantic_context_server.domain.narrative.narrative_memory import NarrativeMemory


class FakeApplicationMemoryService:
    def __init__(self):
        self._store: dict[str, NarrativeMemory] = {}
        self.calls: list[dict] = []

    # ---------------------------------------------------------

    async def load_memory(self, campaign_id: str) -> NarrativeMemory:
        return self._store.get(campaign_id, NarrativeMemory())

    async def save_memory(self, campaign_id: str, memory: NarrativeMemory):
        self._store[campaign_id] = memory

    # ---------------------------------------------------------

    async def append(self, campaign_id: str, text: str):
        self.calls.append({"type": "append", "campaign_id": campaign_id, "text": text})

        if not text:
            return

        memory = await self.load_memory(campaign_id)
        memory.add_event(text)

        self._store[campaign_id] = memory

    # ---------------------------------------------------------

    async def clear(self, campaign_id: str):
        self._store[campaign_id] = NarrativeMemory()
