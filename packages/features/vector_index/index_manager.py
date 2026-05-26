import asyncio
import logging
from typing import Any

from packages.features.vector_index.builder import VectorIndexBuilder

logger = logging.getLogger("semantic_context_server.vector_index.manager")


class VectorIndexManager:
    def __init__(
        self,
        embedding_service: Any,
        storage_backend: Any,
        tokenizer: Any,
        executor: Any,
        semantic_cache_manager: Any,
    ) -> None:
        self.embedding = embedding_service
        self.storage = storage_backend
        self.tokenizer = tokenizer
        self.executor = executor
        self.semantic_cache_manager = semantic_cache_manager

        self._instances: dict[str, Any] = {}

    # ---------------------------------------------------------
    # GET (lazy per campaign)
    # ---------------------------------------------------------
    async def get(self, campaign_id: str) -> Any:
        if campaign_id in self._instances:
            return self._instances[campaign_id]

        storage = self.storage.with_namespace(campaign_id)

        semantic_cache = self.semantic_cache_manager.get(campaign_id)

        vector_index = VectorIndexBuilder(
            embedding_service=self.embedding,
            storage_backend=storage,
            tokenizer=self.tokenizer,
            executor=self.executor,  # Deve ser injetado no Manager via Container
        ).build(
            semantic_cache=semantic_cache,
            campaign_id=campaign_id,
        )

        self._instances[campaign_id] = vector_index

        return vector_index

    # ---------------------------------------------------------
    # OPTIONAL: cleanup
    # ---------------------------------------------------------
    async def clear(self, campaign_id: str) -> None:
        instance = self._instances.pop(campaign_id, None)

        if not instance:
            return

        logger.info("Clearing VectorIndex instance", extra={"campaign_id": campaign_id})

        try:
            # -----------------------------------------------------
            # 🔥 limpeza explícita (se suportado)
            # -----------------------------------------------------
            for method in ["close", "clear", "shutdown", "stop"]:
                if (fn := getattr(instance, method, None)) and callable(fn):
                    if asyncio.iscoroutinefunction(fn):
                        await fn()
                    else:
                        fn()

            # -----------------------------------------------------
            # 🔥 limpeza de componentes internos
            # -----------------------------------------------------
            components = getattr(instance, "components", None)

            if components and hasattr(components, "shutdown"):
                logger.debug("Shutting down components", extra={"campaign_id": campaign_id})
                await components.shutdown()

            logger.info(
                "VectorIndex instance cleared successfully", extra={"campaign_id": campaign_id}
            )

        except Exception:
            logger.exception("Error during VectorIndex cleanup", extra={"campaign_id": campaign_id})
