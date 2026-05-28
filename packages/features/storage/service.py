from __future__ import annotations

from collections.abc import Callable
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
    """Compatibility factory with injected legacy builder from composition root."""

    def __init__(
        self,
        config: Any,
        executor: Any,
        *,
        builder: Callable[[Any, str, Any], Any] | None = None,
    ) -> None:
        self._config = config
        self._executor = executor
        self._builder = builder

    def build(self, campaign_id: str) -> Any:
        if self._builder is None:
            raise RuntimeError("LegacyCampaignStorageFactory requires a storage builder callable.")
        return self._builder(self._config, campaign_id, self._executor)
