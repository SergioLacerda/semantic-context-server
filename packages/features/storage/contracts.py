from __future__ import annotations

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class CampaignStorageFactoryContract(Protocol):
    def build(self, campaign_id: str) -> Any: ...


@runtime_checkable
class CampaignStorageProviderContract(Protocol):
    def get(self, campaign_id: str) -> Any: ...

    def clear(self, campaign_id: str) -> None: ...

    def clear_all(self) -> None: ...
