import pytest

from packages.features.semantic_cache.base_cache import (
    AsyncKVAdapter,
)
from packages.features.semantic_cache.implementations import (
    EmbeddingCache,
    ResponseCache,
    SemanticCache,
)
from tests.config.fakes.infrastructure.storage.fake_kv_store import FakeKVStore


class FakeEmbeddingClient:
    def __init__(self, result=None):
        self.result = result or [0.1, 0.2]
        self.calls = []

    async def embed(self, text: str):
        self.calls.append(text)
        return self.result


@pytest.mark.asyncio
async def test_embedding_cache_get_or_create_uses_client_on_miss():
    client = FakeEmbeddingClient()
    cache = EmbeddingCache(
        kv_store=AsyncKVAdapter(FakeKVStore()),
        client=client,
        ttl=30,
    )

    result = await cache.get_or_create("hello")

    assert result == [0.1, 0.2]
    assert client.calls == ["hello"]


@pytest.mark.asyncio
async def test_embedding_cache_get_or_create_uses_cache_on_hit():
    client = FakeEmbeddingClient()
    cache = EmbeddingCache(
        kv_store=AsyncKVAdapter(FakeKVStore()),
        client=client,
        ttl=30,
    )

    await cache.set("hello", [9, 9, 9])

    result = await cache.get_or_create("hello")

    assert result == [9, 9, 9]
    assert client.calls == []


@pytest.mark.asyncio
async def test_semantic_cache_store_and_search_roundtrip():
    cache = SemanticCache(kv_store=AsyncKVAdapter(FakeKVStore()), ttl=30)

    await cache.store("dragon", ["cave", "treasure"])

    assert await cache.search("dragon") == ["cave", "treasure"]


@pytest.mark.asyncio
async def test_response_cache_behaves_like_base_cache():
    cache = ResponseCache(kv_store=AsyncKVAdapter(FakeKVStore()), ttl=30)

    await cache.set("prompt", {"content": "ok"})

    assert await cache.get("prompt") == {"content": "ok"}
