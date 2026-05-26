# application/services/embedding_strategy.py

import logging
from collections.abc import Iterable, Sequence

from packages.features.embedding_gateway.contracts import (
    EmbeddingGatewayContract as EmbeddingGateway,
)

logger = logging.getLogger("semantic_context_server.embedding.strategy")


class EmbeddingStrategy:
    def __init__(
        self,
        primary: EmbeddingGateway,
        fallback: Sequence[EmbeddingGateway] = (),
    ):
        self.primary = primary
        self.fallback = list(fallback)

    # ---------------------------------------------------------
    # SINGLE
    # ---------------------------------------------------------
    async def embed(self, text: str) -> list[float]:
        providers = [self.primary, *self.fallback]

        last_error: Exception | None = None

        for provider in providers:
            try:
                logger.debug(
                    "Embedding → provider=%s",
                    provider.__class__.__name__,
                )

                return await provider.embed(text)

            except Exception as e:
                last_error = e

                logger.warning(
                    "Embedding failed → provider=%s error=%s",
                    provider.__class__.__name__,
                    str(e),
                    exc_info=True,
                )

        raise RuntimeError("All embedding providers failed") from last_error

    # ---------------------------------------------------------
    # BATCH
    # ---------------------------------------------------------
    async def embed_batch(
        self,
        texts: Iterable[str],
    ) -> list[list[float]]:
        providers = [self.primary, *self.fallback]

        last_error: Exception | None = None

        for provider in providers:
            try:
                logger.debug(
                    "Embedding batch → provider=%s size=%d",
                    provider.__class__.__name__,
                    len(list(texts)),
                )

                return await provider.embed_batch(texts)

            except Exception as e:
                last_error = e

                logger.warning(
                    "Embedding batch failed → provider=%s error=%s",
                    provider.__class__.__name__,
                    str(e),
                    exc_info=True,
                )

        raise RuntimeError("All embedding providers failed") from last_error
