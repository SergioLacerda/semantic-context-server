from pathlib import Path

import pytest

from packages.features.rpg_engine import NarrativeUseCase
from semantic_context_server.domain.narrative.narrative_memory import NarrativeMemory
from semantic_context_server.domain.rag.context_builder import ContextBuilder
from tests.config.fakes.application.memory.fake_memory_service import (
    FakeMemoryService,
)
from tests.config.fakes.infrastructure.llm.fake_llm import DummyLLM
from tests.config.helpers.golden_assert import (
    assert_golden,
    normalize,
)
from tests.utils.assertions import (
    assert_prompt_contains,
    assert_prompt_semantic,
)


@pytest.mark.asyncio
@pytest.mark.golden
async def test_narrative_pipeline_prompt_golden():
    llm = DummyLLM()

    memory_service = FakeMemoryService(history=["open door"])

    context_builder = ContextBuilder(memory_service=memory_service)

    usecase = NarrativeUseCase(
        llm=llm,
        memory_service=memory_service,
        context_builder=context_builder,
    )

    # ---------------------------------------------------------
    # CONTEXT MOCK (controlado)
    # ---------------------------------------------------------

    async def fake_build(*, campaign_id: str, action: str, intent: str = "DEFAULT"):
        return (
            {
                "summary": "",
                "recent_events": ["open door"],
                "history": ["open door"],
                "retrieved": "dark corridor",
                "entities": [],
                "related_entities": [],
                "scene_type": "DEFAULT",
            },
            NarrativeMemory(),
        )

    usecase.context_builder.build = fake_build

    # ---------------------------------------------------------
    # EXECUTION
    # ---------------------------------------------------------

    await usecase.execute(
        campaign_id="c",
        action="enter room",
        user_id="u",
    )

    prompt = normalize(next(req.prompt for req in llm.calls if "Ação do jogador" in req.prompt))

    # ---------------------------------------------------------
    # 🔥 ASSERTS SEMÂNTICOS (CRÍTICOS)
    # ---------------------------------------------------------

    assert_prompt_semantic(prompt)

    assert_prompt_contains(
        prompt,
        "open door",  # memória
        "dark corridor",  # RAG (mockado)
        "enter room",  # ação
    )

    # ---------------------------------------------------------
    # GOLDEN SNAPSHOT
    # ---------------------------------------------------------

    path = Path(__file__).parent / "prompts" / "pipeline.txt"

    assert_golden(path, prompt, update=False)
