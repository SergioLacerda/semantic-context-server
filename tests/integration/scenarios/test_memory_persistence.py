import pytest

from tests.config.harness.scenario_harness import ScenarioHarness
from tests.utils.assertions import assert_any_contains


@pytest.mark.scenario
@pytest.mark.asyncio
async def test_memory_persistence(container_factory):
    scenario = ScenarioHarness()

    await scenario.run_scenario(
        ["pick up key", "open chest"],
        container_factory=container_factory,
    )

    last = scenario.last_result()
    text = str(last)

    assert_any_contains(text, ["key", "chest", "open"])
