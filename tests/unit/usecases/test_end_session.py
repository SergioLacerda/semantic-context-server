import asyncio

import pytest

from semantic_context_server.application.dto.llm_response import LLMResponse
from semantic_context_server.usecases.end_session import EndSessionUseCase
from tests.config.fakes.application.memory.fake_memory_for_end_session import FakeEndSessionMemory
from tests.config.fakes.infrastructure.vector.fake_vector_memory import FakeVectorMemory

# ==========================================================
# HELPERS
# ==========================================================


class StubLLM:
    def __init__(self, content="summary", fail=False):
        self.content = content
        self.fail = fail
        self.calls = []

    async def generate(self, request):
        self.calls.append(request)

        if self.fail:
            raise RuntimeError("LLM failure")

        return LLMResponse(
            content=self.content,
            provider="stub",
            model="stub-model",
        )


def build_usecase(events, llm_content="summary", fail=False):
    memory = FakeEndSessionMemory(events)
    llm = StubLLM(content=llm_content, fail=fail)
    vector_writer = FakeVectorMemory()

    return EndSessionUseCase(memory, llm, vector_writer), memory, vector_writer, llm


def capture_background_tasks(monkeypatch):
    tasks = []
    original = asyncio.create_task

    def fake_create_task(coro):
        task = original(coro)
        tasks.append(task)
        return task

    monkeypatch.setattr(asyncio, "create_task", fake_create_task)
    return tasks


# ==========================================================
# TESTS
# ==========================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_no_events():
    usecase, _, _, _ = build_usecase(events=[])

    result = await usecase.execute("c1")

    assert "Nenhum evento" in result


@pytest.mark.unit
@pytest.mark.asyncio
async def test_empty_extraction(monkeypatch):
    usecase, _, _, _ = build_usecase(events=["event"])

    monkeypatch.setattr(usecase.summarizer, "extract", lambda x: "   ")

    result = await usecase.execute("c1")

    assert "sem eventos relevantes" in result.lower()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_llm_success():
    usecase, memory, _, llm = build_usecase(
        events=["event"],
        llm_content="final summary",
    )

    result = await usecase.execute("c1")

    assert result == "final summary"
    assert memory.cleared is True
    assert len(llm.calls) == 1


@pytest.mark.unit
@pytest.mark.asyncio
async def test_llm_failure_fallback():
    usecase, _, _, _ = build_usecase(
        events=["event"],
        fail=True,
    )

    result = await usecase.execute("c1")

    assert len(result) > 0


@pytest.mark.unit
@pytest.mark.asyncio
async def test_llm_empty_response_fallback():
    usecase, _, _, _ = build_usecase(
        events=["event"],
        llm_content="   ",
    )

    result = await usecase.execute("c1")

    assert len(result) > 0


@pytest.mark.unit
@pytest.mark.asyncio
async def test_vector_writer_called(monkeypatch):
    usecase, _, vector_writer, _ = build_usecase(events=["event"])

    tasks = capture_background_tasks(monkeypatch)

    await usecase.execute("c1")

    await asyncio.gather(*tasks, return_exceptions=True)

    assert vector_writer.calls == [
        {
            "op": "store_event",
            "campaign_id": "c1",
            "texts": ["summary"],
        }
    ]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_memory_cleared_after_success():
    usecase, memory, _, _ = build_usecase(events=["event"])

    await usecase.execute("c1")

    assert memory.cleared is True
    assert memory.events == []
