import pytest

from tests.config.harness.scenario_test_helper import ScenarioTestHelper
from tests.utils.assertions import assert_any_contains

# ==========================================================
# STORY PROGRESSION
# ==========================================================


@pytest.mark.scenario
@pytest.mark.asyncio
async def test_story_progression(container_factory):
    h = ScenarioTestHelper(container_factory)

    await h.run(["grab sword", "attack goblin"])

    last = h.last()
    text = last.get("text", "") if isinstance(last, dict) else str(last)

    assert_any_contains(text, ["attack", "goblin"])


# ==========================================================
# MEMORY PERSISTENCE
# ==========================================================


@pytest.mark.asyncio
async def test_memory_persistence(container_factory):
    h = ScenarioTestHelper(container_factory)

    campaign_id = "c1"

    await h.run(
        ["pick up sword", "use sword"],
        campaign_id=campaign_id,
    )

    await h.assert_memory_not_empty(campaign_id)


# ==========================================================
# ERROR RECOVERY
# ==========================================================


@pytest.mark.scenario
@pytest.mark.asyncio
async def test_error_recovery(container_factory):
    h = ScenarioTestHelper(container_factory)

    result = await h.step("", campaign_id="test")

    text = str(result)

    assert text.strip() != ""


# ==========================================================
# MEMORY WAIT (ASYNC CONSISTENCY)
# ==========================================================


@pytest.mark.asyncio
async def test_memory_eventually_persists(container_factory):
    """
    Garante que memória assíncrona (ex: vector memory)
    eventualmente reflete eventos.
    """
    h = ScenarioTestHelper(container_factory)

    campaign_id = "c_async"

    await h.step("pick up key", campaign_id=campaign_id)

    await h.wait_for_memory(
        "key",
        campaign_id=campaign_id,
    )

    memory = await h.memory(campaign_id)

    assert any("key" in e for e in memory.recent_events)
