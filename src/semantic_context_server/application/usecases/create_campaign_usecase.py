import logging
from typing import Any

logger = logging.getLogger(__name__)


class CreateCampaignUseCase:
    def __init__(self, repository: Any, executor: Any = None) -> None:
        self.repo = repository
        self.executor = executor

    async def execute(self, campaign_id: str) -> bool:
        try:
            # 1. Verifica existência (offload automático via @on_executor no repo)
            exists = await self.repo.exists(campaign_id)
            if exists:
                logger.warning("Attempted to create existing campaign: %s", campaign_id)
                return False

            # 2. Cria estrutura
            await self.repo.create(campaign_id)

            logger.info("Campaign created: %s", campaign_id)
            return True
        except Exception:
            logger.exception("Failed to create campaign %s", campaign_id)
            return False
