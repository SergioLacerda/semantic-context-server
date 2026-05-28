from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Generic, Protocol, TypeVar, runtime_checkable


# ---------------------------------------------------------------------------
# Storage contracts (formerly semantic_context_server.application.ports.storage)
# ---------------------------------------------------------------------------

_T = TypeVar("_T")


@runtime_checkable
class KeyValueStorePort(Protocol, Generic[_T]):
    async def get(self, key: str) -> _T | None: ...
    async def set(self, key: str, value: _T) -> None: ...
    async def delete(self, key: str) -> None: ...
    async def clear(self) -> None: ...


@runtime_checkable
class VectorStorePort(Protocol):
    async def add(
        self,
        doc_id: str,
        vector: list[float],
        metadata: dict[str, Any] | None = None,
    ) -> None: ...
    async def get(self, doc_id: str) -> list[float] | None: ...
    async def search(self, vector: list[float], limit: int = 5) -> list[str]: ...
    async def clear(self) -> None: ...
    async def keys(self) -> list[str]: ...


@runtime_checkable
class DocumentStorePort(Protocol):
    async def set(self, key: str, value: Mapping[str, Any]) -> None: ...
    async def get(self, key: str) -> dict[str, Any] | None: ...
    async def clear(self) -> None: ...


@runtime_checkable
class MetadataStorePort(Protocol):
    async def set(self, key: str, value: dict[str, Any]) -> None: ...
    async def get(self, key: str) -> dict[str, Any] | None: ...
    async def clear(self) -> None: ...


@runtime_checkable
class TokenStorePort(Protocol):
    async def set(self, key: str, value: Any) -> None: ...
    async def get(self, key: str) -> Any: ...
    async def clear(self) -> None: ...


# ---------------------------------------------------------------------------
# Vector index domain contracts
# ---------------------------------------------------------------------------


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
