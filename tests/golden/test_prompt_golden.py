from pathlib import Path

import pytest

from tests.config.helpers.golden_assert import assert_golden
from tests.utils.assertions import (
    assert_prompt_blocks,
    assert_prompt_contains,
    assert_prompt_structure,
    build_prompt,
)

GOLDEN_DIR = Path(__file__).parent / "prompts"
UPDATE_GOLDEN = False


# ==========================================================
# HISTORY (SEM RAG)
# ==========================================================


@pytest.mark.asyncio
@pytest.mark.golden
async def test_prompt_with_history_golden():
    ctx = {
        "scene_type": "DEFAULT",
        "recent_events": ["open door"],
    }

    prompt = build_prompt(ctx, "enter room")

    # ---------------------------------------------------------
    # 🔥 ASSERTS ESTRUTURAIS
    # ---------------------------------------------------------

    assert_prompt_structure(prompt)
    assert_prompt_blocks(prompt)

    # ---------------------------------------------------------
    # 🔥 ASSERTS SEMÂNTICOS
    # ---------------------------------------------------------

    assert_prompt_contains(
        prompt,
        "open door",  # histórico
        "enter room",  # ação
    )

    assert "eventos recentes" in prompt.lower()

    assert "memória relevante" not in prompt.lower()

    # ---------------------------------------------------------
    # GOLDEN
    # ---------------------------------------------------------

    assert_golden(GOLDEN_DIR / "with_history.txt", prompt, update=UPDATE_GOLDEN)


# ==========================================================
# MEMORY (COM RAG)
# ==========================================================


@pytest.mark.asyncio
@pytest.mark.golden
async def test_prompt_with_memory_golden():
    ctx = {
        "scene_type": "DEFAULT",
        "recent_events": ["abriu a porta"],
        "vector_context": ["um cheiro estranho no ar"],
    }

    prompt = build_prompt(ctx, "entrar na sala")

    # ---------------------------------------------------------
    # 🔥 ASSERTS ESTRUTURAIS
    # ---------------------------------------------------------

    assert_prompt_structure(prompt)
    assert_prompt_blocks(prompt)

    # ---------------------------------------------------------
    # 🔥 ASSERTS SEMÂNTICOS
    # ---------------------------------------------------------

    assert_prompt_contains(
        prompt,
        "abriu a porta",
        "um cheiro estranho no ar",
        "entrar na sala",
    )

    assert "memória relevante" in prompt.lower()

    # ---------------------------------------------------------
    # GOLDEN
    # ---------------------------------------------------------

    assert_golden(GOLDEN_DIR / "with_memory.txt", prompt, update=UPDATE_GOLDEN)
