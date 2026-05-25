from typing import Any, Protocol


class VectorReaderPort(Protocol):
    async def search(
        self,
        campaign_id: str,
        query: str,
        k: int = 5,
        filters: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]: ...
