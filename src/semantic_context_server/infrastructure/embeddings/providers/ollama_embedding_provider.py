import asyncio
import logging
from collections.abc import Iterable
from typing import Any, cast

import httpx

from semantic_context_server.application.ports.embedding_gateway import EmbeddingGateway
from semantic_context_server.shared.resilience import resilient_call

logger = logging.getLogger("semantic_context_server.embedding.ollama")


class OllamaEmbeddingProvider(EmbeddingGateway):
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

        # 🔥 padrão correto
        self._dimension: int | None = dimension

        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=self.timeout,
        )

    # ---------------------------------------------------------
    # property
    # ---------------------------------------------------------

    @property
    def dimension(self) -> int | None:
        return self._dimension

    # ---------------------------------------------------------
    # single
    # ---------------------------------------------------------

    async def embed(self, text: str) -> list[float]:
        if not text or not text.strip():
            return self._zero_vector()

        async def call() -> list[float]:
            resp = await self.client.post(
                "/api/embeddings",
                json={
                    "model": self.model,
                    "prompt": text,
                },
            )

            resp.raise_for_status()

            data = resp.json()

            if "embedding" not in data:
                raise RuntimeError("Invalid Ollama response")

            vec: list[float] = data["embedding"]

            # 🔥 lazy dimension
            if self._dimension is None:
                self._dimension = len(vec)

            return vec

        try:
            return cast(list[float], await resilient_call(call, timeout=self.timeout))

        except Exception:
            logger.exception("Ollama embedding failed (len=%s)", len(text))
            raise

    # ---------------------------------------------------------
    # batch (paralelo controlado)
    # ---------------------------------------------------------

    async def embed_batch(
        self,
        texts: Iterable[str],
        *,
        concurrency: int = 4,
    ) -> list[list[float]]:
        texts_list = list(texts)
        if not texts_list:
            return []

        texts_list = [t for t in texts_list if t and t.strip()]
        if not texts_list:
            return []

        semaphore = asyncio.Semaphore(concurrency)

        async def safe_embed(t: str) -> list[float]:
            async with semaphore:
                return await self.embed(t)

        return list(await asyncio.gather(*[safe_embed(t) for t in texts_list]))

    # ---------------------------------------------------------
    # lifecycle
    # ---------------------------------------------------------

    async def close(self) -> None:
        await self.client.aclose()

    # ---------------------------------------------------------
    # helpers
    # ---------------------------------------------------------

    def _zero_vector(self) -> list[float]:
        if self._dimension:
            return [0.0] * self._dimension

        return [0.0] * 384


def create_ollama_embedding(**kwargs: Any) -> OllamaEmbeddingProvider:
    model = kwargs.get("model")
    if not isinstance(model, str):
        raise ValueError("'model' must be a string")
    base_url = kwargs.get("base_url") or "http://localhost:11434"
    return OllamaEmbeddingProvider(
        model=model,
        base_url=base_url,
    )
