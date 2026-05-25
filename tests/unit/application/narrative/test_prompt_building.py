import pytest

from semantic_context_server.domain.rag.context_builder import ContextBuilder
from semantic_context_server.usecases.narrative_event import NarrativeUseCase
from tests.config.fakes.application.memory.fake_memory_service import FakeMemoryService
from tests.config.fakes.infrastructure.llm.fake_llm import DummyLLM
from tests.utils.assertions import (
    assert_prompt_has,
    assert_prompt_semantic,
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
    # CONTEXT CONTROLADO
    # ---------------------------------------------------------

    async def fake_build(**kwargs):
        return (
            {
                "summary": "",
                "recent_events": ["open door"],
                "history": ["open door"],
                "retrieved": "dark corridor",
                "entities": [],
                "related_entities": [],
                "scene_type": "ACTION",
            },
            None,
        )

    usecase.context_builder.build = fake_build

    # ---------------------------------------------------------
    # EXECUÇÃO
    # ---------------------------------------------------------

    await usecase.execute(
        campaign_id="c",
        action="enter room",
        user_id="u",
    )

    request = llm.calls[-1]
    prompt = request.prompt

    # ---------------------------------------------------------
    # 🔥 ASSERTS ESTRUTURAIS
    # ---------------------------------------------------------

    assert_prompt_has(
        prompt,
        "ação do jogador",
    )

    assert_prompt_has(
        prompt,
        "contexto narrativo",
        "eventos recentes",
        "ação do jogador",
    )

    # ---------------------------------------------------------
    # 🔥 ASSERTS SEMÂNTICOS
    # ---------------------------------------------------------

    assert_prompt_semantic(
        prompt,
        "open door",  # memória
        "dark corridor",  # RAG (mockado)
        "enter room",  # ação
    )
