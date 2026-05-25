import pytest

from semantic_context_server.application.services.memory_service import MemoryService
from semantic_context_server.domain.narrative.narrative_memory import NarrativeMemory
from tests.config.fakes.application.memory.fake_memory_repository import (
    FakeMemoryRepository,
)
from tests.config.fakes.infrastructure.llm.fake_llm_service import FakeLLMService

# ==========================================================
# HELPERS
# ==========================================================


def make_memory_data(
    events=None,
    facts=None,
    scene=None,
    summary="",
):
    return {
        "recent_events": events or [],
        "world_facts": facts or [],
        "scene_state": scene or [],
        "summary": summary,
    }


def make_repo(data=None):
    return FakeMemoryRepository({"camp": data or make_memory_data()})


# ==========================================================
# LOAD
# ==========================================================


@pytest.mark.asyncio
async def test_load_memory_with_events():
    repo = make_repo(make_memory_data(events=["event1", "event2"]))

    service = MemoryService(repo, campaign_id="camp")

    memory = await service.load_memory()

    assert memory.recent_events == ["event1", "event2"]


@pytest.mark.asyncio
async def test_load_memory_empty():
    repo = make_repo(make_memory_data())

    service = MemoryService(repo, campaign_id="camp")

    memory = await service.load_memory()

    assert memory.recent_events == []


# ==========================================================
# SAVE
# ==========================================================


@pytest.mark.asyncio
async def test_save_memory():
    repo = FakeMemoryRepository()

    service = MemoryService(repo, campaign_id="camp")

    memory = NarrativeMemory()
    memory.add_event("event1")
    memory.add_event("event2")

    await service.save_memory(memory)

    saved = repo.get_memory("camp")

    assert saved["recent_events"] == ["event1", "event2"]
    assert saved["world_facts"] == []
    assert saved["scene_state"] == []
    assert saved["summary"] == ""


# ==========================================================
# APPEND
# ==========================================================


@pytest.mark.asyncio
async def test_append_new_memory():
    repo = make_repo()

    service = MemoryService(repo, campaign_id="camp")

    await service.append("new event")

    saved = repo.get_memory("camp")

    assert "new event" in saved["recent_events"]


@pytest.mark.asyncio
async def test_append_existing_memory():
    repo = make_repo(make_memory_data(events=["old"]))

    service = MemoryService(repo, campaign_id="camp")

    await service.append("new")

    saved = repo.get_memory("camp")

    assert "old" in saved["recent_events"]
    assert "new" in saved["recent_events"]


@pytest.mark.asyncio
async def test_append_empty_text():
    repo = make_repo()

    service = MemoryService(repo, campaign_id="camp")

    await service.append("")

    saved = repo.get_memory("camp")

    assert saved["recent_events"] == []


# ==========================================================
# OVERFLOW
# ==========================================================


@pytest.mark.asyncio
async def test_append_no_overflow():
    repo = make_repo(make_memory_data(events=["a"]))

    service = MemoryService(repo, campaign_id="camp", max_events=5)

    await service.append("b")

    saved = repo.get_memory("camp")

    assert len(saved["recent_events"]) == 2


@pytest.mark.asyncio
async def test_append_overflow_no_summarizer():
    repo = make_repo(make_memory_data(events=[str(i) for i in range(5)]))

    service = MemoryService(repo, campaign_id="camp", max_events=3)

    await service.append("new")

    saved = repo.get_memory("camp")

    assert len(saved["recent_events"]) == 3


# ==========================================================
# LLM
# ==========================================================


@pytest.mark.asyncio
async def test_append_with_llm_summary():
    repo = make_repo(make_memory_data(events=[str(i) for i in range(5)]))

    service = MemoryService(
        repo,
        campaign_id="camp",
        max_events=3,
        llm_service=FakeLLMService(),
    )

    await service.append("new")

    saved = repo.get_memory("camp")

    assert len(saved["recent_events"]) == 3


# ==========================================================
# CLEAR
# ==========================================================


@pytest.mark.asyncio
async def test_clear_memory():
    repo = make_repo(make_memory_data(events=["a"]))

    service = MemoryService(repo, campaign_id="camp")

    await service.clear()

    saved = repo.get_memory("camp")

    assert saved["recent_events"] == []
    assert saved["world_facts"] == []
    assert saved["scene_state"] == []
    assert saved["summary"] == ""


# ==========================================================
# MISC
# ==========================================================


def test_create_empty():
    service = MemoryService(FakeMemoryRepository(), campaign_id="test")

    mem = service.create_empty()

    assert isinstance(mem, NarrativeMemory)
    assert mem.recent_events == []


def test_compress_short():
    service = MemoryService(FakeMemoryRepository(), campaign_id="test")

    assert service._default_compress("hello") == "hello"


def test_compress_long():
    service = MemoryService(FakeMemoryRepository(), campaign_id="test")

    text = "word " * 100

    result = service._default_compress(text)

    assert len(result) <= 200
