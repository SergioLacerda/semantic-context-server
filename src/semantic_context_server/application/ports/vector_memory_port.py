from typing import Protocol, runtime_checkable


@runtime_checkable
class VectorWriterPort(Protocol):
    async def store_event(
        self,
        campaign_id: str,
        texts: list[str],
        metadata: dict,
    ) -> None: ...
