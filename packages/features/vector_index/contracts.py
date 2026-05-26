from __future__ import annotations

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class VectorStoreContract(Protocol):
    async def search(self, vector: list[float], k: int) -> list[dict[str, Any]]: ...


@runtime_checkable
class VectorIndexContract(Protocol):
    async def search_by_text(self, query: str, k: int = 4) -> list[dict[str, Any]]: ...


@runtime_checkable
class VectorIndexGateway(Protocol):
    async def index_campaign(
        self,
        campaign_id: str,
        texts: list[str],
        metadata: dict[str, Any] | None = None,
    ) -> None: ...

    async def search(self, query: str, k: int = 4) -> list[dict]: ...

    async def search_with_metadata(self, query: str, k: int = 4) -> list[dict]: ...


@runtime_checkable
class VectorWriterPort(Protocol):
    async def store_event(self, campaign_id: str, texts: list[str], metadata: dict) -> None: ...


@runtime_checkable
class VectorReaderPort(Protocol):
    async def search(
        self,
        campaign_id: str,
        query: str,
        k: int = 5,
        filters: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]: ...
