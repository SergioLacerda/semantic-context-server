from collections.abc import Callable
from typing import Any

from tests.config.harness.campaign_harness import CampaignHarness


class ScenarioHarness(CampaignHarness):
    """
    Executa cenários completos.
    """

    def __init__(self):
        super().__init__()
        self.steps: list[dict[str, Any]] = []

    # ---------------------------------------------------------
    # STEP
    # ---------------------------------------------------------

    async def run_step(
        self,
        *,
        campaign_id: str,
        action: str,
        user_id: str = "u1",
        container_factory: Callable[..., Any],
    ):
        campaign = await self.get_campaign(
            campaign_id,
            factory=container_factory,
        )

        result = await campaign.narrative.execute(
            campaign_id=campaign_id,
            action=action,
            user_id=user_id,
        )

        step = {
            "campaign_id": campaign_id,
            "action": action,
            "result": result,
        }

        self.steps.append(step)
        self.record_call(**step)

        return result

    # ---------------------------------------------------------
    # SCENARIO
    # ---------------------------------------------------------

    async def run_scenario(
        self,
        actions: list[str],
        *,
        campaign_id: str = "test",
        user_id: str = "u1",
        container_factory: Callable[..., Any],
    ):
        results = []

        for action in actions:
            results.append(
                await self.run_step(
                    campaign_id=campaign_id,
                    action=action,
                    user_id=user_id,
                    container_factory=container_factory,
                )
            )

        return results

    # ---------------------------------------------------------
    # HELPERS
    # ---------------------------------------------------------

    def last_result(self):
        return self.steps[-1]["result"] if self.steps else None

    def results(self):
        return [s["result"] for s in self.steps]

    def actions_executed(self):
        return [s["action"] for s in self.steps]

    # ---------------------------------------------------------
    # RESET
    # ---------------------------------------------------------

    def reset(self):
        super().reset()
        self.steps.clear()
