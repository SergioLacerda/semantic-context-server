import pytest

from tests.config.harness.scenario_harness import ScenarioHarness
from tests.utils.assertions import assert_not_empty


@pytest.mark.scenario
@pytest.mark.asyncio
async def test_error_recovery(container_factory):
    scenario = ScenarioHarness()

    result = await scenario.run_step(
        campaign_id="test",
        action="",
        container_factory=container_factory,
    )

    assert_not_empty(result)
