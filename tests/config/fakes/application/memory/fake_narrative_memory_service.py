import time
import uuid

from packages.features.rpg_engine.domain.narrative.narrative_memory import NarrativeMemory


class FakeNarrativeMemoryService:
    def __init__(self):
        self._store: dict[str, NarrativeMemory] = {}
        self.calls: list[dict] = []

    # ---------------------------------------------------------

    def load(self, campaign_id: str) -> NarrativeMemory:
        return self._store.get(campaign_id, NarrativeMemory())

    # ---------------------------------------------------------

    def add_event(self, campaign_id: str, text: str):
        self.calls.append({"type": "add_event", "campaign_id": campaign_id, "text": text})

        memory = self.load(campaign_id)

        event = {
            "id": str(uuid.uuid4()),
            "text": text,
            "timestamp": time.time(),
        }

        # aqui usamos API do domínio corretamente
        memory.add_event(text)

        self._store[campaign_id] = memory

        return event

    # ---------------------------------------------------------

    def update_summary(self, campaign_id: str, summary: str):
        memory = self.load(campaign_id)
        memory.update_summary(summary)
        self._store[campaign_id] = memory
