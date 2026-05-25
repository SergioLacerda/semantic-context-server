from collections.abc import Iterable

import pytest

from semantic_context_server.application.ports.embedding_gateway import EmbeddingGateway

# =========================================================
# FAKES
# =========================================================


class DummyEmbeddingGateway(EmbeddingGateway):
    async def embed(self, text: str) -> list[float]:
        return [1.0]

    @property
    def dimension(self) -> int | None:
        return 1

    @property
    def supports_batch(self) -> bool:
        return False


class SpyEmbeddingGateway(EmbeddingGateway):
    def __init__(self) -> None:
        self.calls: list[str] = []

    async def embed(self, text: str) -> list[float]:
        self.calls.append(text)
        return [float(len(text))]

    @property
    def dimension(self) -> int | None:
        return None

    @property
    def supports_batch(self) -> bool:
        return False


class CustomBatchGateway(EmbeddingGateway):
    async def embed(self, text: str) -> list[float]:
        raise AssertionError("embed should not be called")

    async def embed_batch(
        self,
        texts: Iterable[str],
        *,
        concurrency: int = 5,
    ) -> list[list[float]]:
        return [[42.0] for _ in texts]

    @property
    def dimension(self) -> int | None:
        return 1

    @property
    def supports_batch(self) -> bool:
        return True


@pytest.mark.unit
def test_default_properties():
    gateway = SpyEmbeddingGateway()

    assert gateway.dimension is None
    assert gateway.supports_batch is False


@pytest.mark.unit
@pytest.mark.asyncio
async def test_embed_batch_fallback_calls_embed():
    gateway = SpyEmbeddingGateway()

    texts = ["a", "bb", "ccc"]
    result = await gateway.embed_batch(texts)

    assert gateway.calls == texts
    assert result == [[1.0], [2.0], [3.0]]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_embed_batch_empty_input():
    gateway = SpyEmbeddingGateway()

    result = await gateway.embed_batch([])

    assert result == []
    assert gateway.calls == []


@pytest.mark.unit
@pytest.mark.asyncio
async def test_embed_batch_accepts_iterable():
    gateway = SpyEmbeddingGateway()

    texts = (str(i) for i in range(3))

    result = await gateway.embed_batch(texts)

    assert result == [[1.0], [1.0], [1.0]]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_custom_batch_override():
    gateway = CustomBatchGateway()

    result = await gateway.embed_batch(["a", "b"])

    assert result == [[42.0], [42.0]]
