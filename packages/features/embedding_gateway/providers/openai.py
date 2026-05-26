from __future__ import annotations

import logging
from collections.abc import Iterable
from typing import Any, cast

from packages.core.shared_kernel.resilience import resilient_call

try:
    from openai import AsyncOpenAI
except ImportError:
    AsyncOpenAI = None  # type: ignore[assignment,misc]

logger = logging.getLogger("packages.features.embedding_gateway.openai")


class OpenAIEmbeddingProvider:
    supports_batch = True

    def __init__(
        self,
        api_key: str,
        model: str = "text-embedding-3-small",
        timeout: float = 10.0,
        base_url: str | None = None,
    ) -> None:
        if AsyncOpenAI is None:
            raise RuntimeError("openai package not installed")
        self.client = AsyncOpenAI(api_key=api_key, base_url=base_url)
        self.model = model
        self.timeout = timeout
        self._dimension: int | None = None

    @property
    def dimension(self) -> int | None:
        return self._dimension

    def _zero_vector(self) -> list[float]:
        if self._dimension:
            return [0.0] * self._dimension
        return [0.0] * 1536

    async def embed(self, text: str) -> list[float]:
        if not text or not text.strip():
            return self._zero_vector()

        async def call() -> list[float]:
            resp = await self.client.embeddings.create(model=self.model, input=text)
            vec: list[float] = resp.data[0].embedding
            if self._dimension is None:
                self._dimension = len(vec)
            return vec

        try:
            return cast(list[float], await resilient_call(call, timeout=self.timeout))
        except Exception:
            logger.exception("OpenAI embedding failed (len=%s)", len(text))
            raise

    async def embed_batch(
        self,
        texts: Iterable[str],
        *,
        concurrency: int = 5,
    ) -> list[list[float]]:
        texts_list = [t for t in texts if t and t.strip()]
        if not texts_list:
            return []

        async def call() -> list[list[float]]:
            resp = await self.client.embeddings.create(model=self.model, input=texts_list)
            vectors: list[list[float]] = [x.embedding for x in resp.data]
            if self._dimension is None and vectors:
                self._dimension = len(vectors[0])
            return vectors

        try:
            return cast(list[list[float]], await resilient_call(call, timeout=self.timeout))
        except Exception:
            logger.exception("OpenAI batch embedding failed (n=%s)", len(texts_list))
            raise


def create_openai_embedding(**kwargs: Any) -> OpenAIEmbeddingProvider:
    api_key = kwargs.get("api_key")
    if not isinstance(api_key, str):
        raise ValueError("'api_key' must be a string")
    return OpenAIEmbeddingProvider(
        api_key=api_key,
        model=kwargs.get("model") or "text-embedding-3-small",
        base_url=kwargs.get("base_url"),
    )
