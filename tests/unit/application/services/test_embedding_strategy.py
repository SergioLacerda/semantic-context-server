import pytest

from semantic_context_server.application.services.embedding_strategy import EmbeddingStrategy
from tests.config.fakes.infrastructure.retrieval.fake_embedding import DummyEmbedding


@pytest.mark.asyncio
async def test_primary_success():
    primary = DummyEmbedding(result=[1.0])

    strategy = EmbeddingStrategy(primary)

    result = await strategy.embed("hello")

    assert result == [1.0]
    assert primary.called is True


@pytest.mark.asyncio
async def test_primary_failure_fallback_success():
    primary = DummyEmbedding(error=Exception("fail"))
    fallback = DummyEmbedding(result=[2.0])

    strategy = EmbeddingStrategy(primary, [fallback])

    result = await strategy.embed("hello")

    assert result == [2.0]
    assert primary.called is True
    assert fallback.called is True


@pytest.mark.asyncio
async def test_multiple_fallbacks_uses_first_success():
    primary = DummyEmbedding(error=Exception())
    f1 = DummyEmbedding(error=Exception())
    f2 = DummyEmbedding(result=[3.0])
    f3 = DummyEmbedding(result=[4.0])

    strategy = EmbeddingStrategy(primary, [f1, f2, f3])

    result = await strategy.embed("hello")

    assert result == [3.0]
    assert f2.called is True
    assert f3.called is False


@pytest.mark.asyncio
async def test_all_providers_fail():
    primary = DummyEmbedding(error=Exception())
    f1 = DummyEmbedding(error=Exception())
    f2 = DummyEmbedding(error=Exception())

    strategy = EmbeddingStrategy(primary, [f1, f2])

    with pytest.raises(RuntimeError):
        await strategy.embed("hello")


@pytest.mark.asyncio
async def test_fallback_not_called_when_primary_succeeds():
    primary = DummyEmbedding(result=[1.0])
    fallback = DummyEmbedding(result=[2.0])

    strategy = EmbeddingStrategy(primary, [fallback])

    result = await strategy.embed("hello")

    assert result == [1.0]
    assert fallback.called is False


@pytest.mark.asyncio
async def test_no_fallback_configured_and_primary_fails():
    primary = DummyEmbedding(error=Exception())

    strategy = EmbeddingStrategy(primary, [])

    with pytest.raises(RuntimeError):
        await strategy.embed("hello")
