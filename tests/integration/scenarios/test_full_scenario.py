import pytest

from tests.config.harness.scenario_harness import ScenarioHarness
from tests.utils.assertions import assert_any_contains


@pytest.mark.scenario
@pytest.mark.asyncio
async def test_full_scenario(container_factory):
    scenario = ScenarioHarness()

    results = await scenario.run_scenario(
        ["look around", "open door", "attack goblin"],
        container_factory=container_factory,
    )

    assert len(results) == 3
    assert scenario.call_count() == 3

    # 🔥 valida narrativa final
    last = results[-1]
    text = str(last)

    assert_any_contains(text, ["attack", "goblin"])
