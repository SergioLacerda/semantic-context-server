import pytest

from packages.features.rpg_engine import NarrativeUseCase
from tests.config.fakes.application.memory.fake_memory_service import FakeMemoryService


class MockContextBuilder:
    async def build(self, **kwargs):
        return {"scene_type": "default"}, None


class SuccessLLM:
    async def generate(self, request):
        return type("Resp", (), {"content": "You see a forest."})()


def build_usecase(llm):
    return NarrativeUseCase(
        llm=llm,
        memory_service=FakeMemoryService(),
        context_builder=MockContextBuilder(),
    )


# ==========================================================
# TESTS
# ==========================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_narrative_success():
    usecase = build_usecase(SuccessLLM())

    result = await usecase.execute("c1", "look around", "u1")

    assert result.type == "narrative"
    assert "forest" in result.text
    assert result.metadata["scene_type"] == "default"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_narrative_llm_failure_fallback():
    class FailingLLM:
        async def generate(self, request):
            raise Exception("boom")

    usecase = build_usecase(FailingLLM())

    result = await usecase.execute("c1", "attack", "u1")

    assert result.type == "narrative"
    assert result.metadata["fallback"] is True


@pytest.mark.unit
@pytest.mark.asyncio
async def test_llm_returns_none():
    class MockLLM:
        async def generate(self, request):
            return None

    usecase = build_usecase(MockLLM())

    with pytest.raises(RuntimeError, match="LLM returned None"):
        await usecase.execute("c1", "attack", "u1")


@pytest.mark.unit
@pytest.mark.asyncio
async def test_llm_returns_empty():
    class MockLLM:
        async def generate(self, request):
            return type("Resp", (), {"content": "   "})()

    usecase = build_usecase(MockLLM())

    with pytest.raises(RuntimeError):
        await usecase.execute("c1", "attack", "u1")


@pytest.mark.unit
@pytest.mark.asyncio
async def test_llm_returns_none_content():
    class MockLLM:
        async def generate(self, request):
            return type("Resp", (), {"content": None})()

    usecase = build_usecase(MockLLM())

    with pytest.raises(RuntimeError):
        await usecase.execute("c1", "attack", "u1")
