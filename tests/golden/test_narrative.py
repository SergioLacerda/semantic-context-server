from pathlib import Path

import pytest

from tests.config.harness.scenario_test_helper import ScenarioTestHelper
from tests.config.helpers.golden_assert import assert_golden, normalize

GOLDEN_DIR = Path(__file__).parent / "snapshots"
UPDATE_GOLDEN = False

# ==========================================================
# HELPERS
# ==========================================================


def extract_text(result) -> str:
    if isinstance(result, dict):
        return result.get("text", "")
    return str(result)


def build_narrative_snapshot(result) -> str:
    text = extract_text(result)
    return normalize(text)


def assert_narrative_basic(text: str):
    t = text.lower()

    assert len(t) > 0
    assert any(
        k in t
        for k in [
            "attack",
            "goblin",
            "door",
            "room",
        ]
    )


@pytest.mark.asyncio
@pytest.mark.golden
async def test_narrative_attack_goblin(container_factory):
    h = ScenarioTestHelper(container_factory)

    await h.run(["look around", "attack goblin"])

    result = h.last()
    text = build_narrative_snapshot(result)

    # ---------------------------------------------------------
    # ASSERTS SEMÂNTICOS
    # ---------------------------------------------------------

    assert_narrative_basic(text)

    assert "goblin" in text

    # ---------------------------------------------------------
    # GOLDEN
    # ---------------------------------------------------------

    assert_golden(
        GOLDEN_DIR / "attack_goblin.txt",
        text,
        update=UPDATE_GOLDEN,
    )


@pytest.mark.asyncio
@pytest.mark.golden
async def test_narrative_with_memory(container_factory):
    h = ScenarioTestHelper(container_factory)

    await h.run(
        ["pick up key", "open chest"],
        campaign_id="mem_test",
    )

    result = h.last()
    text = build_narrative_snapshot(result)

    # ---------------------------------------------------------
    # ASSERTS SEMÂNTICOS
    # ---------------------------------------------------------

    assert "key" in text or "chest" in text

    # ---------------------------------------------------------
    # GOLDEN
    # ---------------------------------------------------------

    assert_golden(
        GOLDEN_DIR / "memory_interaction.txt",
        text,
        update=UPDATE_GOLDEN,
    )
