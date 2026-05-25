import pytest

from semantic_context_server.domain.narrative.narrative_memory import NarrativeMemory
from semantic_context_server.domain.rag.context_builder import ContextBuilder
from semantic_context_server.usecases.narrative_event import NarrativeUseCase
from tests.config.fakes.application.memory.fake_memory_service import FakeMemoryService
from tests.config.fakes.infrastructure.llm.fake_llm import DummyLLM
from tests.utils.assertions import (
    assert_min_length,
    assert_not_contains_semantic,
    assert_semantic,
)


@pytest.mark.asyncio
async def test_narrative_calls_llm():
    llm = DummyLLM()

    memory_service = FakeMemoryService(history=["look around"])
    context_builder = ContextBuilder(memory_service=memory_service)

    usecase = NarrativeUseCase(
        llm=llm,
        memory_service=memory_service,
        context_builder=context_builder,
    )

    # ---------------------------------------------------------
    # CONTEXT MOCK
    # ---------------------------------------------------------

    async def fake_build(**kwargs):
        return (
            {
                "summary": "",
                "recent_events": ["look around"],
                "history": ["look around"],
                "retrieved": "",
                "entities": [],
                "related_entities": [],
                "scene_type": "ACTION",
                "intent": "ACTION",
            },
            NarrativeMemory(),
        )

    usecase.context_builder.build = fake_build

    # ---------------------------------------------------------
    # EXECUTION
    # ---------------------------------------------------------

    result = await usecase.execute(
        campaign_id="c",
        action="open door",
        user_id="u",
    )

    # ---------------------------------------------------------
    # ASSERTS
    # ---------------------------------------------------------

    assert_semantic(result, "door", "open", "enter")
    assert_not_contains_semantic(result, "permanece incerto")
    assert_min_length(result, 2)
