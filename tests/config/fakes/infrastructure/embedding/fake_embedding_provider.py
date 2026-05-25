import hashlib

from semantic_context_server.application.ports.embedding_gateway import EmbeddingGateway
from tests.utils.spy import spy_on


class FakeEmbeddingProvider(EmbeddingGateway):
    def __init__(self, dim: int = 8):
        self.dim = dim
        self.calls: list[dict] = []
        self._fail_with: Exception | None = None

    @property
    def dimension(self) -> int:
        return self.dim

    @property
    def supports_batch(self) -> bool:
        return True

    def _simulate_failure(self, error: Exception):
        """Configura o fake para lançar uma exceção nas próximas chamadas."""
        self._fail_with = error

    # ---------------------------------------------------------
    # SINGLE
    # ---------------------------------------------------------

    @spy_on
    async def embed(self, text: str) -> list[float]:
        if self._fail_with:
            raise self._fail_with

        return self._vectorize(text)

    # ---------------------------------------------------------
    # BATCH
    # ---------------------------------------------------------

    @spy_on
    async def embed_batch(
        self,
        texts: list[str],
        *,
        concurrency: int = 5,
        **kwargs,
    ) -> list[list[float]]:
        if self._fail_with:
            raise self._fail_with

        return [self._vectorize(t) for t in texts]

    # ---------------------------------------------------------
    # INTERNAL
    # ---------------------------------------------------------

    def _vectorize(self, text: str) -> list[float]:
        if not text:
            return [0.0] * self.dim

        h = hashlib.sha256(text.encode()).digest()

        return [h[i] / 255.0 for i in range(self.dim)]
