from __future__ import annotations

import asyncio
import logging
from collections.abc import Iterable
from typing import Any, cast

import httpx

from packages.core.shared_kernel.resilience import resilient_call

logger = logging.getLogger("packages.features.embedding_gateway.ollama")


class OllamaEmbeddingProvider:
    supports_batch = False

    def __init__(
        self,
        model: str,
        base_url: str = "http://localhost:11434",
        timeout: float = 15.0,
        dimension: int | None = None,
    ) -> None:
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._dimension: int | None = dimension
        self.client = httpx.AsyncClient(base_url=self.base_url, timeout=self.timeout)

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
            resp = await self.client.post(
                "/api/embeddings",
                json={"model": self.model, "prompt": text},
            )
            resp.raise_for_status()
            data = resp.json()
            if "embedding" not in data:
                raise RuntimeError("Invalid Ollama response")
            vec: list[float] = data["embedding"]
            if self._dimension is None:
                self._dimension = len(vec)
            return vec

        try:
            return cast(list[float], await resilient_call(call, timeout=self.timeout))
        except Exception:
            logger.exception("Ollama embedding failed (len=%s)", len(text))
            raise

    async def embed_batch(
        self,
        texts: Iterable[str],
        *,
        concurrency: int = 4,
    ) -> list[list[float]]:
        texts_list = [t for t in texts if t and t.strip()]
        if not texts_list:
            return []

        semaphore = asyncio.Semaphore(concurrency)

        async def safe_embed(t: str) -> list[float]:
            async with semaphore:
                return await self.embed(t)

        return list(await asyncio.gather(*[safe_embed(t) for t in texts_list]))

    async def close(self) -> None:
        await self.client.aclose()


def create_ollama_embedding(**kwargs: Any) -> OllamaEmbeddingProvider:
    model = kwargs.get("model")
    if not isinstance(model, str):
        raise ValueError("'model' must be a string")
    return OllamaEmbeddingProvider(
        model=model,
        base_url=kwargs.get("base_url") or "http://localhost:11434",
    )
