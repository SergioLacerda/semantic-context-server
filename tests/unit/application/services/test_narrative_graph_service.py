import pytest

from semantic_context_server.application.services.narrative_graph_service import (
    NarrativeGraphService,
)
from tests.config.fakes.domain.graph.fake_graph_repository import FakeGraphRepository
from tests.config.fakes.domain.narrative.fake_extractor import FakeExtractor


@pytest.mark.asyncio
async def test_update_from_event_uses_default_campaign_and_persists_graph():
    extractor = FakeExtractor(["dragon", "castle"])
    repo = FakeGraphRepository()

    service = NarrativeGraphService(repo, extractor)

    await service.update_from_event("dragon in castle")

    assert extractor.called_with == "dragon in castle"
    assert repo.loaded_campaign == "default"
    assert repo.saved is not None

    campaign_id, graph = repo.saved

    assert campaign_id == "default"
    assert graph.updated_entities == ["dragon", "castle"]
    assert graph.updated_text == "dragon in castle"
    assert graph.updated_context == {}


@pytest.mark.asyncio
async def test_update_from_event_with_explicit_campaign_and_context():
    extractor = FakeExtractor(["dragon"])
    repo = FakeGraphRepository()

    service = NarrativeGraphService(repo, extractor)

    await service.update_from_event(
        campaign_id="c1",
        text="dragon attacks",
        context={"location": "castle"},
    )

    assert repo.loaded_campaign == "c1"
    assert repo.saved is not None

    campaign_id, graph = repo.saved

    assert campaign_id == "c1"
    assert graph.updated_entities == ["dragon"]
    assert graph.updated_text == "dragon attacks"
    assert graph.updated_context == {"location": "castle"}


@pytest.mark.asyncio
async def test_update_from_event_without_entities_does_not_persist():
    extractor = FakeExtractor([])
    repo = FakeGraphRepository()

    service = NarrativeGraphService(repo, extractor)

    await service.update_from_event("...")

    assert repo.loaded_campaign == "default"
    assert repo.saved is None


@pytest.mark.asyncio
async def test_related_extracts_entities_from_query_and_returns_set():
    extractor = FakeExtractor(["dragon"])
    repo = FakeGraphRepository()
    repo.graph.set_related_result(["castle", "treasure"])

    service = NarrativeGraphService(repo, extractor)

    result = await service.related("dragon")

    assert extractor.called_with == "dragon"
    assert repo.loaded_campaign == "default"
    assert result == {"castle", "treasure"}
    assert repo.graph.related_query == "dragon"


@pytest.mark.asyncio
async def test_related_with_explicit_campaign_and_entities():
    extractor = FakeExtractor(["should not be used"])
    repo = FakeGraphRepository()
    repo.graph.set_related_result(["castle"])

    service = NarrativeGraphService(repo, extractor)

    result = await service.related(campaign_id="c1", entities=["dragon", "knight"])

    assert extractor.called_with is None
    assert repo.loaded_campaign == "c1"
    assert result == {"castle"}
    assert repo.graph.related_query == "dragon knight"


@pytest.mark.asyncio
async def test_related_without_entities_returns_empty_set():
    extractor = FakeExtractor([])
    repo = FakeGraphRepository()

    service = NarrativeGraphService(repo, extractor)

    result = await service.related("...")

    assert repo.loaded_campaign is None
    assert result == set()
