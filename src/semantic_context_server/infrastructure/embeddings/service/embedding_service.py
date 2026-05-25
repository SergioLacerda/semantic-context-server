import asyncio
import logging
from collections.abc import Iterable, Sequence
from typing import Any, cast

from semantic_context_server.application.ports.embedding_gateway import EmbeddingGateway
from semantic_context_server.infrastructure.embeddings.core.fallback import (
    deterministic_vector,
)
from semantic_context_server.shared.resilience import resilient_call

logger = logging.getLogger("semantic_context_server.embedding")


class EmbeddingService(EmbeddingGateway):
    def __init__(
        self,
        providers: Sequence[EmbeddingGateway],
        target_dim: int = 1536,
        cache: Any = None,
        strict: bool = False,
        max_concurrency: int = 8,
        executor: Any = None,
        retries: int = 2,
        timeout: float = 180.0,
    ) -> None:
        self.providers = list(providers)
        self.target_dim = target_dim
        self.cache = cache
        self.strict = strict
        self.executor = executor
        self.timeout = timeout
        self.retries = retries

        self._semaphore = asyncio.Semaphore(max_concurrency)

    @property
    def dimension(self) -> int:
        return self.target_dim

    @property
    def supports_batch(self) -> bool:
        return True

    # -----------------------------------------
    # internal
    # -----------------------------------------

    def _fallback(self, text: str) -> list[float]:
        logger.debug("Embedding fallback → deterministic")
        return deterministic_vector(text, self.target_dim)

    async def _call_provider(self, provider: EmbeddingGateway, text: str) -> list[float]:
        async with self._semaphore:
            result = await resilient_call(
                provider.embed,
                text,
                timeout=self.timeout,
                executor=self.executor,
                retries=self.retries,
            )

            if result is None:
                raise RuntimeError(f"Provider {provider.__class__.__name__} returned None")

            return cast(list[float], result)

    def _validate_vector(self, vec: list[float], provider_name: str) -> list[float]:
        if not isinstance(vec, list):
            raise RuntimeError(f"{provider_name} returned invalid vector type")

        if not vec:
            raise RuntimeError(f"{provider_name} returned empty vector")

        if len(vec) != self.target_dim:
            logger.warning(
                "Embedding dimension mismatch → provider=%s got=%d expected=%d",
                provider_name,
                len(vec),
                self.target_dim,
            )
            if self.strict:
                raise RuntimeError(f"Dimension mismatch from {provider_name}")

        return vec

    # -----------------------------------------
    # single
    # -----------------------------------------

    async def embed(self, text: str) -> list[float]:
        text = (text or "").strip()

        if not text:
            return self._fallback(text)

        # cache
        if self.cache:
            cached = await self.cache.get(text)
            if cached:
                logger.debug("Embedding cache hit")
                return cast(list[float], cached)

        # providers
        for provider in self.providers:
            name = provider.__class__.__name__

            try:
                logger.debug("Embedding attempt → %s", name)

                vec = await self._call_provider(provider, text)
                vec = self._validate_vector(vec, name)

                if self.cache:
                    await self.cache.set(text, vec)

                logger.info("Embedding success → %s", name)

                return vec

            except Exception:
                logger.warning("Embedding failed → %s", name, exc_info=True)

        if self.strict:
            raise RuntimeError("All embedding providers failed")

        logger.error("Embedding fallback triggered")

        vec = self._fallback(text)

        if self.cache:
            await self.cache.set(text, vec)

        return vec

    # -----------------------------------------
    # batch
    # -----------------------------------------

    async def embed_batch(self, texts: Iterable[str], *, concurrency: int = 5) -> list[list[float]]:
        texts = [(t or "").strip() for t in texts]

        if not texts:
            return []

        for provider in self.providers:
            if getattr(provider, "supports_batch", False):
                name = provider.__class__.__name__

                try:
                    logger.debug("Batch embedding → %s", name)

                    # Passa a concorrência solicitada para o provedor
                    vectors = await resilient_call(
                        provider.embed_batch,
                        texts,
                        concurrency=concurrency,
                        timeout=self.timeout,
                        executor=self.executor,
                    )

                    if vectors is None:
                        raise RuntimeError(f"Batch provider {name} returned None")

                    validated = [self._validate_vector(v, name) for v in vectors]

                    logger.info("Batch embedding success → %s", name)

                    return validated

                except Exception:
                    logger.warning("Batch provider failed → %s", name, exc_info=True)

        logger.debug("Batch fallback → parallel single calls")

        # Gather com proteção de timeout global
        tasks = [self.embed(t) for t in texts]
        try:
            return await asyncio.wait_for(
                asyncio.gather(*tasks),
                timeout=self.timeout + 5,  # Margem para o gather
            )
        except TimeoutError:
            logger.error("Batch embedding gather timed out")
            return [self._fallback(t) for t in texts]
