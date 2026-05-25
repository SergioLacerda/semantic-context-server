from collections.abc import Iterable


class DummyEmbedding:
    def __init__(
        self,
        *,
        result: list[float] | None = None,
        error: Exception | None = None,
    ):
        self._result = result or [0.0]
        self._error = error
        self.called = False

    # ---------------------------------------------------------
    # PORT
    # ---------------------------------------------------------
    @property
    def dimension(self) -> int:
        return len(self._result)

    @property
    def supports_batch(self) -> bool:
        return True

    # ---------------------------------------------------------
    # API
    # ---------------------------------------------------------
    async def embed(self, text: str) -> list[float]:
        self.called = True

        if self._error:
            raise self._error

        return self._result

    async def embed_batch(
        self,
        texts: Iterable[str],
        *,
        concurrency: int = 1,
    ) -> list[list[float]]:
        self.called = True

        if self._error:
            raise self._error

        return [self._result for _ in texts]
