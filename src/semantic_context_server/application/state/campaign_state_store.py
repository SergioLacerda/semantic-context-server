from typing import Any


class CampaignStateStore:
    """Persistent campaign state backed by a JSON KV store.

    Each channel_id maps directly to a campaign_id key in the KV store.
    """

    def __init__(self, kv_store: Any) -> None:
        self._kv = kv_store

    async def get(self, channel_id: str) -> str | None:
        try:
            result: str | None = await self._kv.get(channel_id)
            return result
        except Exception:
            return None

    async def set(self, channel_id: str, campaign_id: str) -> None:
        await self._kv.set(channel_id, campaign_id)

    async def delete(self, channel_id: str) -> None:
        await self._kv.delete(channel_id)
