import asyncio

import pytest

from packages.features.vector_index.retrieval_engine import RetrievalEngine
from tests.config.fakes.infrastructure.retrieval import (
    DummyIndex,
)


class AsyncDummyEmbeddingCache:
    def __init__(self):
        self.data = {}

    async def get(self, k):
        return self.data.get(k)

    async def set(self, k, v):
        self.data[k] = v


class AsyncDummySemanticCache:
    def __init__(self):
        self.data = {}

    async def get(self, q, v):
        return self.data.get(q)

    async def set(self, q, v, r):
        self.data[q] = r


class MockEmbeddingService:
    def embed(self, text: str):
        return [0.1, 0.2]


class FakeIndex:
    def __init__(self, result):
        self.result = result
        self.calls = 0

    async def search(self, query, q_vec, k):
        self.calls += 1
        return self.result


class SyncIndex:
    def __init__(self, result):
        self.result = result
        self.calls = 0

    def search(self, query, q_vec, k):
        self.calls += 1
        return self.result


@pytest.fixture
def engine():
    index = DummyIndex()
    return RetrievalEngine(
        vector_index=index,
        embedding_service=MockEmbeddingService(),
        embedding_cache=AsyncDummyEmbeddingCache(),
        semantic_cache=AsyncDummySemanticCache(),
    )


@pytest.mark.asyncio
async def test_search_basic(engine):
    result = await engine.search("hello", k=2)

    assert result == ["result:hello:2"]


@pytest.mark.asyncio
async def test_search_uses_semantic_cache(engine):
    r1 = await engine.search("hello")
    r2 = await engine.search("hello")

    assert r1 == r2
    assert len(engine.default_index.calls) == 1


@pytest.mark.asyncio
async def test_inflight_deduplication(engine):
    async def call():
        return await engine.search("same")

    results = await asyncio.gather(call(), call(), call())

    assert all(r == results[0] for r in results)
    assert len(engine.default_index.calls) == 1


@pytest.mark.asyncio
async def test_index_factory_usage():
    indexes = {}

    def factory(campaign_id):
        idx = DummyIndex()
        indexes[campaign_id] = idx
        return idx

    engine = RetrievalEngine(
        vector_index=DummyIndex(),
        embedding_service=MockEmbeddingService(),
        embedding_cache=AsyncDummyEmbeddingCache(),
        semantic_cache=AsyncDummySemanticCache(),
        vector_index_factory=factory,
    )

    await engine.search("q1", campaign_id="A")
    await engine.search("q2", campaign_id="A")

    assert "A" in indexes
    assert len(indexes["A"].calls) == 2


@pytest.mark.asyncio
async def test_default_index_when_no_factory(engine):
    await engine.search("hello")

    assert len(engine.default_index.calls) == 1


@pytest.mark.asyncio
async def test_multiple_campaign_indexes():
    calls = {}

    def factory(cid):
        idx = DummyIndex()
        calls[cid] = idx
        return idx

    engine = RetrievalEngine(
        vector_index=DummyIndex(),
        embedding_service=MockEmbeddingService(),
        embedding_cache=AsyncDummyEmbeddingCache(),
        semantic_cache=AsyncDummySemanticCache(),
        vector_index_factory=factory,
    )

    await engine.search("q1", campaign_id="A")
    await engine.search("q1", campaign_id="B")

    assert calls["A"] is not calls["B"]


@pytest.mark.asyncio
async def test_semantic_cache_skips_search(engine):
    await engine.semantic_cache.set("q", [1, 2], ["cached"])

    result = await engine.search("q")

    assert result == ["cached"]
    assert len(engine.default_index.calls) == 0


@pytest.mark.asyncio
async def test_get_index_default():
    from packages.features.vector_index.retrieval_engine import RetrievalEngine

    index = FakeIndex(["ok"])

    engine = RetrievalEngine(
        vector_index=index,
        embedding_service=MockEmbeddingService(),
        embedding_cache=AsyncDummyEmbeddingCache(),
        semantic_cache=AsyncDummySemanticCache(),
    )

    result = await engine.search("q")

    assert result == ["ok"]


@pytest.mark.asyncio
async def test_get_index_with_factory():
    from packages.features.vector_index.retrieval_engine import RetrievalEngine

    def factory(cid):
        return FakeIndex([cid])

    engine = RetrievalEngine(
        vector_index=FakeIndex(["default"]),
        embedding_service=MockEmbeddingService(),
        embedding_cache=AsyncDummyEmbeddingCache(),
        semantic_cache=AsyncDummySemanticCache(),
        vector_index_factory=factory,
    )

    result = await engine.search("q", campaign_id="c1")

    assert result == ["c1"]


@pytest.mark.asyncio
async def test_semantic_cache_hit():
    from packages.features.vector_index.retrieval_engine import RetrievalEngine

    cache = AsyncDummySemanticCache()
    await cache.set("q", None, ["cached"])

    engine = RetrievalEngine(
        vector_index=FakeIndex(["real"]),
        embedding_service=MockEmbeddingService(),
        embedding_cache=AsyncDummyEmbeddingCache(),
        semantic_cache=cache,
    )

    result = await engine.search("q")

    assert result == ["cached"]


@pytest.mark.asyncio
async def test_inflight_dedup():
    from packages.features.vector_index.retrieval_engine import RetrievalEngine

    index = FakeIndex(["ok"])

    engine = RetrievalEngine(
        vector_index=index,
        embedding_service=MockEmbeddingService(),
        embedding_cache=AsyncDummyEmbeddingCache(),
        semantic_cache=AsyncDummySemanticCache(),
    )

    results = await asyncio.gather(
        engine.search("q"),
        engine.search("q"),
    )

    assert results[0] == ["ok"]
    assert index.calls == 1


@pytest.mark.asyncio
async def test_execute_with_executor():
    from packages.features.vector_index.retrieval_engine import RetrievalEngine

    class FakeExecutor:
        async def run(self, fn, *args, **kwargs):
            return fn(*args, **kwargs)

    index = SyncIndex(["ok"])

    engine = RetrievalEngine(
        vector_index=index,
        embedding_service=MockEmbeddingService(),
        embedding_cache=AsyncDummyEmbeddingCache(),
        semantic_cache=AsyncDummySemanticCache(),
        executor=FakeExecutor(),
    )

    result = await engine.search("q")

    assert result == ["ok"]


@pytest.mark.slow
@pytest.mark.asyncio
async def test_hedged_search():
    from packages.features.vector_index.retrieval_engine import RetrievalEngine

    class SlowIndex:
        async def search(self, query, q_vec, k):
            await asyncio.sleep(0.05)
            return ["slow"]

    engine = RetrievalEngine(
        vector_index=SlowIndex(),
        embedding_service=MockEmbeddingService(),
        embedding_cache=AsyncDummyEmbeddingCache(),
        semantic_cache=AsyncDummySemanticCache(),
        enable_hedging=True,
        hedge_delay=0.01,
    )

    result = await engine.search("q")

    assert result == ["slow"]


@pytest.mark.asyncio
async def test_inflight_cleanup():
    from packages.features.vector_index.retrieval_engine import RetrievalEngine

    index = FakeIndex(["ok"])

    engine = RetrievalEngine(
        vector_index=index,
        embedding_service=MockEmbeddingService(),
        embedding_cache=AsyncDummyEmbeddingCache(),
        semantic_cache=AsyncDummySemanticCache(),
    )

    await engine.search("q")

    assert len(engine._inflight) == 0


@pytest.mark.asyncio
async def test_get_index_cached_instance():
    from packages.features.vector_index.retrieval_engine import RetrievalEngine

    calls = {"count": 0}

    class AsyncCache:
        def __init__(self):
            self.data = {}

        async def get(self, *args):
            return self.data.get(args[0])

        async def set(self, k, v, r):
            self.data[k] = r

    class MockIdx:
        def __init__(self):
            self.calls = 0

        async def search(self, *args, **kwargs):
            self.calls += 1
            return ["ok"]

    def factory(cid):
        calls["count"] += 1
        return MockIdx()

    # Usamos caches locais assíncronos para evitar conflitos com fakes globais
    emb_cache = AsyncCache()
    sem_cache = AsyncCache()

    engine = RetrievalEngine(
        vector_index=MockIdx(),
        embedding_service=MockEmbeddingService(),
        embedding_cache=emb_cache,
        semantic_cache=sem_cache,
        vector_index_factory=factory,
    )

    await engine.search("q1", campaign_id="A")
    await engine.search("q2", campaign_id="A")

    assert calls["count"] == 1


@pytest.mark.asyncio
async def test_execute_index_sync_without_executor():
    index = SyncIndex(["ok"])

    engine = RetrievalEngine(
        vector_index=index,
        embedding_service=MockEmbeddingService(),
        embedding_cache=AsyncDummyEmbeddingCache(),
        semantic_cache=AsyncDummySemanticCache(),
        executor=None,
    )

    result = await engine.search("q")

    assert result == ["ok"]
    assert index.calls == 1


@pytest.mark.asyncio
async def test_execute_raises_and_not_cached():
    class FailingIndex:
        async def search(self, query, q_vec, k):
            raise RuntimeError("boom")

    cache = AsyncDummySemanticCache()

    engine = RetrievalEngine(
        vector_index=FailingIndex(),
        embedding_service=MockEmbeddingService(),
        embedding_cache=AsyncDummyEmbeddingCache(),
        semantic_cache=cache,
    )

    with pytest.raises(RuntimeError):
        await engine.search("q")

    assert "q" not in cache.data


@pytest.mark.asyncio
async def test_inflight_cleanup_on_error():
    class FailingIndex:
        async def search(self, query, q_vec, k):
            raise RuntimeError("boom")

    engine = RetrievalEngine(
        vector_index=FailingIndex(),
        embedding_service=MockEmbeddingService(),
        embedding_cache=AsyncDummyEmbeddingCache(),
        semantic_cache=AsyncDummySemanticCache(),
    )

    with pytest.raises(RuntimeError):
        await engine.search("q")

    assert len(engine._inflight) == 0
