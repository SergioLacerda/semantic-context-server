from collections.abc import Callable
from typing import Any

from tests.config.harness.base_harness import BaseHarness


class CampaignHarness(BaseHarness):
    """
    Harness base para campanhas.

    ✔ resolve CampaignContainer corretamente
    ✔ injeta fakes automaticamente
    ✔ mantém isolamento por campanha
    ✔ compatível com nova arquitetura (writer/reader)
    """

    def __init__(self):
        super().__init__()
        self._root_container = None
        self._campaigns: dict[str, Any] = {}

    # ---------------------------------------------------------
    # ROOT
    # ---------------------------------------------------------

    def _get_root(self, factory: Callable[..., Any]):
        if self._root_container is None:
            self._root_container = factory()
        return self._root_container

    # ---------------------------------------------------------
    # CAMPAIGN
    # ---------------------------------------------------------

    async def get_campaign(
        self,
        campaign_id: str,
        *,
        factory: Callable[..., Any],
    ):
        if campaign_id not in self._campaigns:
            root = self._get_root(factory)

            campaign = root.campaigns.get(campaign_id)

            if hasattr(campaign, "__await__"):
                campaign = await campaign

            self._inject_fakes(root, campaign)

            self._campaigns[campaign_id] = campaign

        return self._campaigns[campaign_id]

    # ---------------------------------------------------------
    # INJECTION
    # ---------------------------------------------------------

    def _inject_fakes(self, root, campaign):
        """
        Injeta fakes de forma segura e compatível com nova arquitetura.

        ✔ Injeta apenas serviços de aplicação
        """

        state = getattr(root, "_state", None)

        if not state:
            return

        # --------------------------------------------------
        # MEMORY
        # --------------------------------------------------
        if hasattr(state, "memory"):
            campaign._memory_service = state.memory

        # --------------------------------------------------
        # CONTEXT
        # --------------------------------------------------
        if hasattr(state, "context"):
            campaign._context_service = state.context

        # --------------------------------------------------
        # INTENT
        # --------------------------------------------------
        if hasattr(state, "intent"):
            campaign._intent_classifier = state.intent

        # --------------------------------------------------
        # ⚠️ VECTOR NÃO É INJETADO
        # --------------------------------------------------
        # writer/reader são lazy e já isolados por campanha
        # qualquer override deve ser feito no ContainerBuilder

    # ---------------------------------------------------------
    # ALIAS
    # ---------------------------------------------------------

    async def get_container(
        self,
        campaign_id: str,
        *,
        factory: Callable[..., Any],
    ):
        return await self.get_campaign(campaign_id, factory=factory)

    # ---------------------------------------------------------
    # RESET
    # ---------------------------------------------------------

    def reset(self):
        super().reset()
        self._campaigns.clear()
        self._root_container = None
