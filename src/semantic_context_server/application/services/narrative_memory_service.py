import time
import uuid
from collections.abc import Callable
from typing import Any

from semantic_context_server.domain.narrative.narrative_memory import NarrativeMemory


class NarrativeMemoryService:
    """
    Orquestra memória narrativa + helpers para indexação.
    """

    def __init__(
        self,
        repo: Any,
        campaign_id: str,
        now_fn: Callable[[], float] = time.time,
        id_fn: Callable[[], str] = lambda: str(uuid.uuid4()),
    ) -> None:
        self.repo = repo
        self.campaign_id = campaign_id
        self._now = now_fn
        self._id = id_fn

    # ---------------------------------------------------------
    # leitura
    # ---------------------------------------------------------

    async def load(self) -> NarrativeMemory:
        result: NarrativeMemory = await self.repo.load(self.campaign_id)
        return result

    # ---------------------------------------------------------
    # helpers
    # ---------------------------------------------------------

    def now(self) -> float:
        return self._now()

    def generate_event_id(self) -> str:
        return self._id()

    async def get_last_event_id(self) -> str | None:
        memory = await self.repo.load(self.campaign_id)

        # Ajustado de .events para .recent_events para alinhar com o domínio
        if not memory.recent_events:
            return None

        result_id: str | None = memory.recent_events[-1].get("id")
        return result_id

    # ---------------------------------------------------------
    # update
    # ---------------------------------------------------------

    async def add_event(self, text: str) -> dict[str, Any]:
        memory = await self.repo.load(self.campaign_id)

        event = {
            "id": self.generate_event_id(),
            "text": text,
            "timestamp": self.now(),
        }

        memory.add_event(event)

        await self.repo.save(self.campaign_id, memory)

        return event

    async def update_summary(self, summary: str) -> None:
        memory = await self.repo.load(self.campaign_id)

        memory.update_summary(summary)

        await self.repo.save(self.campaign_id, memory)

    # ---------------------------------------------------------
    # NLP simples (MVP)
    # ---------------------------------------------------------

    def extract_tokens(self, text: str) -> list[str]:
        return [token.lower() for token in text.split() if len(token) > 2]
