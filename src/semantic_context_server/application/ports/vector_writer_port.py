from typing import Protocol


class VectorWriterPort(Protocol):
    async def store_event(
        self,
        campaign_id: str,
        texts: list[str],
        metadata: dict,
    ) -> None: ...
