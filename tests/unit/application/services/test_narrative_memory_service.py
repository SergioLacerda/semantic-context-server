import uuid
from typing import Any

import pytest

from semantic_context_server.application.services.narrative_memory_service import (
    NarrativeMemoryService,
)
from tests.config.fakes.application.memory.fake_memory_repository import FakeMemoryRepository


@pytest.fixture
def repo():
    from packages.features.rpg_engine.domain.narrative.narrative_memory import NarrativeMemory

    class NarrativeMemoryMock(FakeMemoryRepository):
        def __init__(self):
            super().__init__()
            self.memory = NarrativeMemory()
            self.saved_memory: NarrativeMemory | None = None

        async def load(self, campaign_id: str) -> Any:
            return self.memory

        async def save(self, campaign_id: str, data):
            self.saved_memory = data

    return NarrativeMemoryMock()


@pytest.fixture
def service(repo):
    return NarrativeMemoryService(repo, campaign_id="test-campaign")


@pytest.mark.asyncio
async def test_load_returns_memory(service, repo):
    assert await service.load() is repo.memory


def test_now_returns_float(service):
    assert isinstance(service.now(), float)


def test_generate_event_id_is_valid_uuid(service):
    event_id = service.generate_event_id()

    assert str(uuid.UUID(event_id)) == event_id


@pytest.mark.asyncio
async def test_get_last_event_id_empty(service):
    assert await service.get_last_event_id() is None


@pytest.mark.asyncio
async def test_get_last_event_id_returns_last(service, repo):
    repo.memory.add_event({"id": "1"})
    repo.memory.add_event({"id": "2"})

    assert await service.get_last_event_id() == "2"


@pytest.mark.asyncio
async def test_add_event_creates_and_saves(service, repo):
    event = await service.add_event("dragon appears")

    assert repo.memory.recent_events[0] == event
    assert repo.saved_memory is repo.memory


@pytest.mark.asyncio
async def test_update_summary_updates_and_saves(service, repo):
    await service.update_summary("new summary")

    assert repo.memory.summary == "new summary"
    assert repo.saved_memory is repo.memory


def test_extract_tokens_basic(service):
    assert service.extract_tokens("The Dragon is BIG") == ["the", "dragon", "big"]


def test_extract_tokens_removes_short_words(service):
    assert service.extract_tokens("a an the big dragon") == ["the", "big", "dragon"]


@pytest.mark.asyncio
async def test_add_event_deterministic(repo):
    service = NarrativeMemoryService(
        repo,
        campaign_id="test",
        now_fn=lambda: 123.0,
        id_fn=lambda: "fixed-id",
    )

    event = await service.add_event("test")

    assert event == {
        "id": "fixed-id",
        "text": "test",
        "timestamp": 123.0,
    }
