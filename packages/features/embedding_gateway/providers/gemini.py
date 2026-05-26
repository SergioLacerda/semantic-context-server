from __future__ import annotations

import asyncio
import logging
from collections.abc import Iterable
from typing import Any, cast

from packages.core.shared_kernel.resilience import resilient_call

try:
    import google.generativeai as genai
except ImportError:
    genai = None

logger = logging.getLogger("packages.features.embedding_gateway.gemini")


class GeminiEmbeddingProvider:
    supports_batch = False

    def __init__(
        self,
        api_key: str,
        model: str = "models/embedding-001",
        timeout: float = 10.0,
        dimension: int | None = None,
    ) -> None:
        if genai is None:
            raise RuntimeError("google-generativeai not installed")
        genai.configure(api_key=api_key)
        self.model = model
        self.timeout = timeout
        self._dimension: int | None = dimension

    @property
    def dimension(self) -> int | None:
        return self._dimension

    def _zero_vector(self) -> list[float]:
        if self._dimension:
            return [0.0] * self._dimension
        return [0.0] * 768

    async def embed(self, text: str) -> list[float]:
        if not text or not text.strip():
            return self._zero_vector()

        def _call() -> Any:
            assert genai is not None
            return genai.embed_content(model=self.model, content=text)

        async def call() -> list[float]:
            resp = await asyncio.wait_for(asyncio.to_thread(_call), timeout=self.timeout)
            vec: list[float] = resp["embedding"]
            if self._dimension is None:
                self._dimension = len(vec)
            return vec

        try:
            return cast(list[float], await resilient_call(call))
        except Exception:
            logger.exception("Gemini embedding failed (len=%s)", len(text))
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

        semaphore = asyncio.Semaphore(concurrency)

        async def safe_embed(t: str) -> list[float]:
            async with semaphore:
                return await self.embed(t)

        return list(await asyncio.gather(*[safe_embed(t) for t in texts_list]))


def create_gemini_embedding(**kwargs: Any) -> GeminiEmbeddingProvider:
    api_key = kwargs.get("api_key")
    if not isinstance(api_key, str):
        raise ValueError("'api_key' must be a string")
    return GeminiEmbeddingProvider(
        api_key=api_key,
        model=kwargs.get("model") or "models/embedding-001",
    )
