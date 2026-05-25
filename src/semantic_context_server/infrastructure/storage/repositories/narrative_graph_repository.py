import contextlib
from typing import Any

from semantic_context_server.application.ports.storage import KeyValueStorePort


class NarrativeGraphRepository:
    def __init__(self, kv: KeyValueStorePort[Any], *, world: str = "default") -> None:
        self.kv = kv
        self.world = world

    def _key(self, campaign_id: str) -> str:
        return f"{self.world}:{campaign_id}:narrative_graph"

    # ---------------------------------------------------------
    # load
    # ---------------------------------------------------------

    async def load(self, campaign_id: str) -> dict[str, Any]:
        try:
            data = await self.kv.get(self._key(campaign_id))
            return data or {}
        except Exception:
            return {}

    # ---------------------------------------------------------
    # save
    # ---------------------------------------------------------

    async def save(self, campaign_id: str, graph: dict[str, Any]) -> None:
        with contextlib.suppress(Exception):
            await self.kv.set(self._key(campaign_id), graph)
