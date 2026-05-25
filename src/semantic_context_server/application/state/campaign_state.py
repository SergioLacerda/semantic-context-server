class CampaignState:
    """Maps channel IDs to active campaign IDs (in-memory)."""

    def __init__(self) -> None:
        self._data: dict[str, str] = {}

    def get(self, channel_id: str) -> str | None:
        return self._data.get(channel_id)

    def set(self, channel_id: str, campaign_id: str) -> None:
        self._data[channel_id] = campaign_id

    def clear(self, channel_id: str) -> None:
        self._data.pop(channel_id, None)

    def delete(self, channel_id: str) -> None:
        self._data.pop(channel_id, None)
