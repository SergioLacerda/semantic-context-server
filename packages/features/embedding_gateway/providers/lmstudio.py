from __future__ import annotations

import logging
from typing import cast

import httpx

from packages.core.shared_kernel.resilience import resilient_call

try:
    from openai import AsyncOpenAI
except ImportError:
    AsyncOpenAI = None  # type: ignore[assignment,misc]

logger = logging.getLogger("packages.features.embedding_gateway.lmstudio")


class LMStudioEmbeddingProvider:
    supports_batch = True

    def __init__(
        self,
        model: str,
        base_url: str = "http://localhost:1234/v1",
        timeout: float = 180.0,
    ) -> None:
        if AsyncOpenAI is None:
            raise ImportError("AsyncOpenAI not available. Install openai package.")
        self.model = model
        self.timeout = timeout
        self.client = AsyncOpenAI(
            base_url=base_url,
            api_key="lmstudio",
            timeout=httpx.Timeout(timeout),
        )
        self._dimension: int | None = None

    @property
    def dimension(self) -> int | None:
        return self._dimension

    def _zero_vector(self) -> list[float]:
        if self._dimension:
            return [0.0] * self._dimension
        return [0.0] * 384

    async def embed(self, text: str) -> list[float]:
        if not text or not text.strip():
            return self._zero_vector()

        async def call() -> list[float]:
            resp = await self.client.embeddings.create(model=self.model, input=text)
            return resp.data[0].embedding

        try:
            result = await resilient_call(call, timeout=self.timeout)
            if not isinstance(result, list):
                raise TypeError("Invalid embedding response")
            return cast(list[float], result)
        except Exception:
            logger.exception("LMStudio embedding failed (len=%s)", len(text))
            raise

    async def embed_batch(self, texts: list[str], *, concurrency: int = 5) -> list[list[float]]:
        texts = [t for t in texts if t and t.strip()]
        if not texts:
            return []

        async def call() -> list[list[float]]:
            response = await self.client.embeddings.create(model=self.model, input=texts)
            return [x.embedding for x in response.data]

        try:
            result = await resilient_call(call, timeout=self.timeout)
            if not isinstance(result, list):
                raise TypeError("Invalid batch embedding response")
            return cast(list[list[float]], result)
        except Exception:
            logger.exception("LMStudio batch embedding failed (n=%s)", len(texts))
            raise


def create_lmstudio_embedding(
    model: str,
    base_url: str = "http://localhost:1234/v1",
    timeout: float = 180.0,
) -> LMStudioEmbeddingProvider:
    return LMStudioEmbeddingProvider(model=model, base_url=base_url, timeout=timeout)
