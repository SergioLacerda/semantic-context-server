from __future__ import annotations

from typing import Any

from packages.features.storage.contracts import CampaignStorageFactoryContract


class CampaignStorageService:
    """Package-level campaign storage provider with lazy per-campaign caching."""

    def __init__(self, factory: CampaignStorageFactoryContract) -> None:
        self._factory = factory
        self._cache: dict[str, Any] = {}

    def get(self, campaign_id: str) -> Any:
        if campaign_id not in self._cache:
            self._cache[campaign_id] = self._factory.build(campaign_id)
        return self._cache[campaign_id]

    def clear(self, campaign_id: str) -> None:
        self._cache.pop(campaign_id, None)

    def clear_all(self) -> None:
        self._cache.clear()


class LegacyCampaignStorageFactory:
    """Compatibility factory that delegates to current legacy storage builder."""

    def __init__(self, config: Any, executor: Any) -> None:
        self._config = config
        self._executor = executor

    def build(self, campaign_id: str) -> Any:
        from semantic_context_server.infrastructure.storage.campaign_storage_factory import (
            build_campaign_storage,
        )

        return build_campaign_storage(self._config, campaign_id, self._executor)
