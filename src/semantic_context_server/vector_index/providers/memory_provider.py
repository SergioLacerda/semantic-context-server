from typing import Any


class MemoryProvider:
    """
    Adapter entre sistema principal e vector_index.
    """

    def __init__(self, campaign_repository: Any) -> None:
        self.repo = campaign_repository

    def get_recent(self, limit: int = 10) -> list[str]:
        # sync wrapper simples
        events = self.repo.get_events_sync(limit=limit)

        return [e.get("text", "") for e in events if e.get("text")]
