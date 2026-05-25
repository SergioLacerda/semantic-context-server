import logging
from typing import Any

logger = logging.getLogger(__name__)


class DeleteCampaignUseCase:
    def __init__(
        self, repository: Any, campaign_scoped_container: Any, executor: Any = None
    ) -> None:
        self.repo = repository
        self.campaigns = campaign_scoped_container
        self.executor = executor

    async def execute(self, campaign_id: str) -> bool:
        # Verifica existência (I/O via Executor)
        exists = await self.repo.exists(campaign_id)
        if not exists:
            return False

        # 1. Encerra o runtime primeiro (Lifecycle Safe)
        await self.campaigns.clear(campaign_id)

        # 2. Deleta os dados persistentes (Arquivos/DB)
        await self.repo.delete(campaign_id)

        logger.info("Campaign deleted: %s", campaign_id)

        return True
