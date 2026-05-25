import logging
from typing import Any

logger = logging.getLogger(__name__)


class ListCampaignsUseCase:
    def __init__(self, repo: Any, executor: Any = None) -> None:
        self.repo = repo
        self.executor = executor

    async def execute(self) -> list[str]:
        try:
            # O repositório já gerencia o executor via @on_executor
            return await self.repo.list() or []
        except Exception:
            logger.exception("Failed to list campaigns")
            return []
