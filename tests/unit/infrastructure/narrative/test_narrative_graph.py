import pytest

from semantic_context_server.application.services.narrative_graph_service import (
    NarrativeGraphService,
)
from tests.config.fakes.domain.graph.fake_graph import FakeGraph
from tests.config.fakes.domain.graph.fake_graph_repository import FakeGraphRepository
from tests.config.fakes.domain.narrative.fake_extractor import FakeExtractor

# ==========================================================
# UPDATE
# ==========================================================


@pytest.mark.asyncio
async def test_update_from_event_with_entities():
    extractor = FakeExtractor({"dragon", "castle"})
    graph = FakeGraph()
    repo = FakeGraphRepository(graph=graph)

    service = NarrativeGraphService(repo=repo, extractor=extractor)

    await service.update_from_event("dragon in castle")

    assert extractor.called_with == "dragon in castle"
    assert graph.updated_text == "dragon in castle"
    assert repo.saved is not None


@pytest.mark.asyncio
async def test_update_from_event_without_entities():
    extractor = FakeExtractor(set())
    graph = FakeGraph()
    repo = FakeGraphRepository(graph=graph)

    service = NarrativeGraphService(repo=repo, extractor=extractor)

    await service.update_from_event("...")

    assert extractor.called_with == "..."
    assert graph.updated_text is None
    assert repo.saved is None


# ==========================================================
# RELATED
# ==========================================================


@pytest.mark.asyncio
async def test_related_with_entities():
    extractor = FakeExtractor({"dragon"})
    graph = FakeGraph()
    graph.set_related_result({"fire"})

    repo = FakeGraphRepository(graph=graph)

    service = NarrativeGraphService(repo=repo, extractor=extractor)

    result = await service.related("dragon")

    assert extractor.called_with == "dragon"
    assert graph.related_query == "dragon"
    assert result == ["fire"]


@pytest.mark.asyncio
async def test_related_without_entities():
    extractor = FakeExtractor(set())
    graph = FakeGraph()
    repo = FakeGraphRepository(graph=graph)

    service = NarrativeGraphService(repo=repo, extractor=extractor)

    result = await service.related("...")

    assert extractor.called_with == "..."
    assert result == []


# ==========================================================
# EDGE CASES
# ==========================================================


@pytest.mark.asyncio
async def test_related_graph_returns_empty():
    extractor = FakeExtractor({"dragon"})
    graph = FakeGraph()
    graph.set_related_result(set())

    repo = FakeGraphRepository(graph=graph)

    service = NarrativeGraphService(repo=repo, extractor=extractor)

    result = await service.related("dragon")

    assert result == []


@pytest.mark.asyncio
async def test_multiple_updates_accumulate():
    extractor = FakeExtractor({"dragon"})
    graph = FakeGraph()
    repo = FakeGraphRepository(graph=graph)

    service = NarrativeGraphService(repo=repo, extractor=extractor)

    await service.update_from_event("dragon 1")
    await service.update_from_event("dragon 2")

    assert graph.updated_text == "dragon 2"
    assert repo.saved is not None


# ==========================================================
# EXTRA ROBUSTNESS
# ==========================================================


@pytest.mark.asyncio
async def test_update_requires_text():
    extractor = FakeExtractor({"dragon"})
    graph = FakeGraph()
    repo = FakeGraphRepository(graph=graph)

    service = NarrativeGraphService(repo=repo, extractor=extractor)

    await service.update_from_event("")

    assert graph.updated_text is None
    assert repo.saved is None


@pytest.mark.asyncio
async def test_related_requires_campaign_and_entities():
    extractor = FakeExtractor([])
    graph = FakeGraph()
    repo = FakeGraphRepository(graph=graph)

    service = NarrativeGraphService(repo=repo, extractor=extractor)

    result = await service.related("")

    assert result == []
