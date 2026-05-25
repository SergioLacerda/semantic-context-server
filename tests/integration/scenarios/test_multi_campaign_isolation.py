import pytest

from tests.config.harness.scenario_harness import ScenarioHarness


@pytest.mark.scenario
@pytest.mark.asyncio
async def test_multi_campaign_isolation(container_factory):
    scenario = ScenarioHarness()

    await scenario.run_step(
        campaign_id="c1",
        action="take sword",
        container_factory=container_factory,
    )

    await scenario.run_step(
        campaign_id="c2",
        action="take shield",
        container_factory=container_factory,
    )

    assert len(scenario.calls) == 2

    campaigns = {c["campaign_id"] for c in scenario.calls}

    assert campaigns == {"c1", "c2"}
