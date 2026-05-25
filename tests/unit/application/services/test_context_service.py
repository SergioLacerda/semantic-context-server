import pytest

from semantic_context_server.application.services.context_service import ContextService
from tests.config.factories.framework.context_deps import (
    FakeEmbeddingCache,
    FakeNarrativeGraph,
    FakeVectorReader,
)


@pytest.mark.asyncio
async def test_search_returns_texts():
    # Setup com leitores separados para campanha e mundo
    campaign_reader = FakeVectorReader([{"text": "doc_camp"}])
    world_reader = FakeVectorReader([{"text": "doc_world"}])

    service = ContextService(
        vector_reader_campaign=campaign_reader, vector_reader_world=world_reader
    )

    result = await service.search("c1", "dragon")

    assert "doc_camp" in result
    assert "doc_world" in result


@pytest.mark.asyncio
async def test_search_passes_query_and_k():
    campaign_reader = FakeVectorReader([])
    service = ContextService(vector_reader_campaign=campaign_reader)

    # O service multiplica k * 3 internamente para o safe_search
    await service.search("c1", "dragon", k=5)

    assert campaign_reader.called_with == ("c1", "dragon", 15)


@pytest.mark.asyncio
async def test_query_expansion_via_graph():
    campaign_reader = FakeVectorReader([])
    graph = FakeNarrativeGraph(related_entities=["fire", "cave"])

    service = ContextService(vector_reader_campaign=campaign_reader, narrative_graph=graph)

    await service.search("c1", "dragon")

    # Verifica se a query expandida foi enviada ao reader
    # A expansão junta a query original com até 3 entidades
    _, expanded_query, _ = campaign_reader.called_with
    assert "dragon" in expanded_query
    assert "fire" in expanded_query or "cave" in expanded_query


@pytest.mark.asyncio
async def test_ranking_with_embeddings_and_weights():
    # doc de campanha costuma ter peso maior (1.0 vs 0.6)
    # Adicionando documentos extras para garantir que result tenha tamanho >= k (2)
    campaign_reader = FakeVectorReader(
        [{"text": "history of dragon"}, {"text": "campaign secondary context"}]
    )
    world_reader = FakeVectorReader([{"text": "general lore"}, {"text": "world secondary lore"}])
    cache = FakeEmbeddingCache()

    service = ContextService(
        vector_reader_campaign=campaign_reader,
        vector_reader_world=world_reader,
        embedding_cache=cache,
    )

    # Usando intent LORE que favorece o world_reader (weight 1.0)
    result = await service.search("c1", "lore", intent="LORE", k=2)

    assert result[0] == "general lore"
    assert result[1] == "history of dragon"


@pytest.mark.asyncio
async def test_search_preserves_order():
    campaign_reader = FakeVectorReader(
        [
            {"text": "a"},
            {"text": "b"},
            {"text": "c"},
        ]
    )

    service = ContextService(vector_reader_campaign=campaign_reader)

    result = await service.search("c1", "q")

    assert result == ["a", "b", "c"]


@pytest.mark.asyncio
async def test_search_skips_missing_text_key():
    campaign_reader = FakeVectorReader([{"text": "ok"}, {"metadata_only": "fail"}])
    service = ContextService(vector_reader_campaign=campaign_reader)

    result = await service.search("c1", "q")
    assert result == ["ok"]
