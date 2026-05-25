import asyncio
from types import SimpleNamespace

import pytest

from semantic_context_server.infrastructure.rag.vector_writer_service import (
    VectorWriterService,
)
from tests.config.fakes.infrastructure.storage.fake_kv_store import FakeKVStore


class MockVectorStore:
    def __init__(self):
        self.calls = []

    def add(self, doc_id, emb):
        self.calls.append((doc_id, emb))


def build_adapter(embedding, embedding_cache=None):
    vector_index = SimpleNamespace(
        vector_store=MockVectorStore(),
        embedding_service=embedding,
        components=SimpleNamespace(
            document_store=FakeKVStore(),
            metadata_store=FakeKVStore(),
        ),
    )

    return VectorWriterService(
        vector_index,
        embedding_cache=embedding_cache,
        managed=True,
    )


def build_adapter_full(batch_size=2, flush_interval=0.01, embedding_cache=None):
    vs = MockVectorStore()
    ds = FakeKVStore()
    ms = FakeKVStore()

    vector_index = SimpleNamespace(
        vector_store=vs,
        embedding_service=SimpleNamespace(
            embed=lambda t: (1,),
        ),
        components=SimpleNamespace(
            document_store=ds,
            metadata_store=ms,
        ),
    )

    return (
        VectorWriterService(
            vector_index,
            embedding_cache=embedding_cache,
            batch_size=batch_size,
            flush_interval=flush_interval,
            managed=True,
        ),
        vs,
        ds,
        ms,
    )


def make_event(adapter, cid, text, metadata):
    return {
        "id": adapter._generate_id(cid, text),
        "campaign_id": cid,
        "text": text,
        "metadata": metadata,
    }


@pytest.mark.unit
def test_requires_managed_construction():
    vector_index = SimpleNamespace(
        vector_store=MockVectorStore(),
        embedding_service=SimpleNamespace(embed=lambda t: (1,)),
        components=SimpleNamespace(
            document_store=FakeKVStore(),
            metadata_store=FakeKVStore(),
        ),
    )

    with pytest.raises(RuntimeError, match="managed=True"):
        VectorWriterService(vector_index)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_embed_batch_falls_back_to_sync_embed():
    class Emb:
        def embed(self, text):
            return (3,)

    adapter = build_adapter(Emb())

    result = await adapter._embed_batch(["a", "b"])

    assert result == [(3,), (3,)]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_embed_batch_falls_back_to_async_embed():
    class Emb:
        async def embed(self, text):
            return (4,)

    adapter = build_adapter(Emb())

    result = await adapter._embed_batch(["a"])

    assert result == [(4,)]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_embed_batch_prefers_embedding_cache():
    class FailingEmb:
        def embed(self, text):
            raise AssertionError("embed should not be called when cache hits")

    class Cache:
        async def get_many(self, texts):
            return [(7,)] * len(texts)

    adapter = build_adapter(FailingEmb(), embedding_cache=Cache())

    result = await adapter._embed_batch(["a", "b"])

    assert result == [(7,), (7,)]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_flush_writes_all_stores():
    adapter, vs, ds, ms = build_adapter_full()

    batch = [
        make_event(adapter, "c1", "hello world", {"a": 1}),
        make_event(adapter, "c1", "another event", {"b": 2}),
    ]

    await adapter._flush(batch)

    assert len(vs.calls) == 2
    assert len(ds._store) == 2
    assert len(ms._store) == 2


@pytest.mark.unit
@pytest.mark.asyncio
async def test_flush_skips_existing_document():
    adapter, vs, ds, ms = build_adapter_full()
    event = make_event(adapter, "c1", "hello world", {"a": 1})
    await ds.set(event["id"], {"text": "already exists"})

    await adapter._flush([event])

    assert vs.calls == []
    assert ms._store == {}


@pytest.mark.unit
@pytest.mark.asyncio
async def test_flush_empty():
    adapter, *_ = build_adapter_full()

    await adapter._flush([])


@pytest.mark.unit
def test_generate_id():
    adapter, *_ = build_adapter_full()

    doc_id = adapter._generate_id("c1", "hello world")

    assert doc_id.startswith("c1:")


@pytest.mark.unit
def test_generate_id_is_deterministic():
    adapter, *_ = build_adapter_full()

    id1 = adapter._generate_id("c1", "hello")
    id2 = adapter._generate_id("c1", "hello")

    assert id1 == id2


@pytest.mark.unit
def test_generate_id_is_campaign_scoped():
    adapter, *_ = build_adapter_full()

    id1 = adapter._generate_id("c1", "hello")
    id2 = adapter._generate_id("c2", "hello")

    assert id1 != id2


@pytest.mark.unit
def test_generate_id_changes_with_text():
    adapter, *_ = build_adapter_full()

    id1 = adapter._generate_id("c1", "a")
    id2 = adapter._generate_id("c1", "b")

    assert id1 != id2


@pytest.mark.unit
@pytest.mark.asyncio
async def test_store_event_requires_started_service():
    adapter, *_ = build_adapter_full()

    with pytest.raises(RuntimeError, match="started"):
        await adapter.store_event("c1", ["valid event"], {"x": 1})


@pytest.mark.unit
@pytest.mark.asyncio
async def test_store_event_enqueue_filters_short_texts():
    adapter, *_ = build_adapter_full()
    await adapter.start()

    try:
        await adapter.store_event("c1", ["a", "valid event"], {"x": 1})

        assert adapter._queue.qsize() == 1
    finally:
        await adapter.shutdown()


@pytest.mark.unit
@pytest.mark.slow
@pytest.mark.asyncio
async def test_worker_flush_by_batch():
    adapter, vs, *_ = build_adapter_full(batch_size=2, flush_interval=10)

    await adapter.start()

    try:
        await adapter.store_event("c1", ["valid event one", "valid event two"], {})
        await asyncio.sleep(0.1)
    finally:
        await adapter.shutdown()

    assert len(vs.calls) >= 2


@pytest.mark.unit
@pytest.mark.slow
@pytest.mark.asyncio
async def test_worker_flush_by_timeout():
    adapter, vs, *_ = build_adapter_full(batch_size=10, flush_interval=0.01)

    await adapter.start()

    try:
        await adapter.store_event("c1", ["valid event"], {})
        await asyncio.sleep(0.05)
    finally:
        await adapter.shutdown()

    assert len(vs.calls) >= 1


@pytest.mark.unit
@pytest.mark.asyncio
async def test_start_idempotent():
    adapter, *_ = build_adapter_full()

    await adapter.start()
    await adapter.start()

    await adapter.shutdown()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_shutdown_without_start():
    adapter, *_ = build_adapter_full()

    await adapter.shutdown()
