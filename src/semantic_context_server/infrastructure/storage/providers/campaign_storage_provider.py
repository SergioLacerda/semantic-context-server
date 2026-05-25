from typing import Any

from semantic_context_server.application.ports.executor import ExecutorPort
from semantic_context_server.application.ports.storage_config import StorageConfigPort
from semantic_context_server.infrastructure.storage.campaign_storage_factory import (
    build_campaign_storage,
)


class CampaignStorageProvider:
    def __init__(self, config: StorageConfigPort, executor: ExecutorPort) -> None:
        self.config = config
        self.executor = executor
        self._cache: dict[str, Any] = {}

    def get(self, campaign_id: str) -> Any:
        if campaign_id not in self._cache:
            self._cache[campaign_id] = build_campaign_storage(
                self.config,
                campaign_id,
                self.executor,
            )

        return self._cache[campaign_id]

    def clear(self, campaign_id: str) -> None:
        self._cache.pop(campaign_id, None)

    def clear_all(self) -> None:
        self._cache.clear()
