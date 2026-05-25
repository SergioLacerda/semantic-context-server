import pytest

from semantic_context_server.application.services.retrieval_pipeline import (
    RetrievalService,
)
from tests.config.fakes.infrastructure.vector.fake_vector_index import (
    FakeVectorIndex as BaseFakeVectorIndex,
)


class FakeVectorIndex(BaseFakeVectorIndex):
    """
    Concrete implementation of FakeVectorIndex to satisfy the VectorIndexGateway interface.
    """

    async def search_with_metadata(self, query: str, k: int = 4):
        return []


class FakeEmbeddingGateway:
    async def embed(self, text: str, *_, **__):
        return [0.1] * 32

    async def embed_batch(self, texts, *_, **__):
        return [[0.1] * 32 for _ in texts]


class FakeContextWindow:
    def __init__(self, vector_index):
        self.vector_index = vector_index
        self.called_with = None

    async def search(self, query, k=4):
        self.called_with = (query, k)

        results = await self.vector_index.search_async(query, k)
        return [r["text"] for r in results]

    def get_policy(self, action: str) -> dict:
        """Return a default policy for the given action."""
        return {"max_docs": 5}

    def apply(self, docs, policy):
        """Apply the policy to limit the documents and extract text."""
        if not docs:
            return []
        max_docs = policy.get("max_docs", 5)
        docs = docs[:max_docs]
        # Extract text from each document
        return [d["text"] if isinstance(d, dict) else d for d in docs]


class DummySelector:
    def select(self, docs):
        return docs[:1]


def build_service(vi, context_window):
    return RetrievalService(
        vector_index=vi,
        embedding_gateway=FakeEmbeddingGateway(),
        campaign_id="default",
        planner=None,
        context_window=context_window,
        selector=DummySelector(),
    )


@pytest.mark.asyncio
async def test_retrieval_pipeline_flow():
    vi = FakeVectorIndex()
    await vi.index_campaign("default", ["dragon fire", "ice spell", "dragon cave"])

    context_window = FakeContextWindow(vi)
    service = build_service(vi, context_window)

    result = await service.search("dragon")

    assert result == ["dragon fire"]


@pytest.mark.asyncio
async def test_search_passes_k_correctly():
    vi = FakeVectorIndex()
    await vi.index_campaign("default", ["doc1", "doc2"])

    context_window = FakeContextWindow(vi)
    service = build_service(vi, context_window)

    await service.search("test", k=10)

    assert context_window.called_with == ("test", 10)


@pytest.mark.asyncio
async def test_selector_limits_results():
    vi = FakeVectorIndex()
    await vi.index_campaign("default", ["a", "b", "c", "d"])

    context_window = FakeContextWindow(vi)
    service = build_service(vi, context_window)

    result = await service.search("a")

    assert len(result) == 1


@pytest.mark.asyncio
async def test_empty_index_returns_empty():
    vi = FakeVectorIndex()

    context_window = FakeContextWindow(vi)
    service = build_service(vi, context_window)

    result = await service.search("anything")

    assert result == []


@pytest.mark.asyncio
async def test_context_window_is_called():
    vi = FakeVectorIndex()
    await vi.index_campaign("default", ["doc1"])

    context_window = FakeContextWindow(vi)
    service = build_service(vi, context_window)

    await service.search("doc")

    assert context_window.called_with is not None
