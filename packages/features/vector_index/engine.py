from typing import Any


class SearchContext:
    def __init__(
        self,
        query: str,
        q_vec: list[float] | None,
        query_tokens: list[str],
        query_type: str | None,
        vector_store: Any,
        k: int = 4,
        token_store: Any | None = None,
        metadata_store: Any | None = None,
        ann: Any | None = None,
        temporal_index: Any | None = None,
    ) -> None:
        self.query = query
        self.q_vec = q_vec
        self.query_tokens = query_tokens
        self.query_type = query_type

        self.vector_store = vector_store
        self.token_store = token_store
        self.metadata_store = metadata_store

        self.k = k

        self.ann = ann
        self.temporal_index = temporal_index

        # 🔥 pipeline state
        self.candidates: list[Any] = []
        self.results: list[Any] = []

        # caches
        self._token_cache: dict[str, Any] = {}
        self._meta_cache: dict[str, Any] = {}

    # ==========================================================
    # VECTOR
    # ==========================================================
    def get_vector(self, doc_id: str) -> Any:
        if not self.vector_store:
            return None

        if hasattr(self.vector_store, "get"):
            return self.vector_store.get(doc_id)

        return None

    # ==========================================================
    # TOKENS (cached)
    # ==========================================================
    def get_tokens(self, doc_id: str) -> Any:
        if doc_id in self._token_cache:
            return self._token_cache[doc_id]

        tokens = None
        if self.token_store and hasattr(self.token_store, "get"):
            tokens = self.token_store.get(doc_id)

        self._token_cache[doc_id] = tokens
        return tokens

    # ==========================================================
    # METADATA (cached)
    # ==========================================================
    def get_metadata(self, doc_id: str) -> Any:
        if doc_id in self._meta_cache:
            return self._meta_cache[doc_id]

        meta = None
        if self.metadata_store and hasattr(self.metadata_store, "get"):
            meta = self.metadata_store.get(doc_id)

        self._meta_cache[doc_id] = meta
        return meta

    # ==========================================================
    # ADD RESULT (pipeline-safe)
    # ==========================================================
    def add_result(self, item: Any) -> None:
        if item is None:
            return

        self.results.append(item)

    # ==========================================================
    # ADD CANDIDATE
    # ==========================================================
    def add_candidate(self, item: Any) -> None:
        if item is None:
            return

        self.candidates.append(item)

    # ==========================================================
    # FINALIZE RESULTS
    # ==========================================================
    def finalize(self) -> "SearchContext":
        """
        Normaliza resultados finais para garantir:
        - presença de texto
        - deduplicação
        - limite k
        """

        seen = set()
        normalized = []

        for r in self.results:
            if isinstance(r, dict):
                text = r.get("text") or r.get("content") or ""
                score = r.get("score", 0.0)
            else:
                text = getattr(r, "text", str(r))
                score = getattr(r, "score", 0.0)

            if not text:
                continue

            if text in seen:
                continue
            seen.add(text)

            normalized.append(
                {
                    "text": text,
                    "score": float(score),
                }
            )

        normalized.sort(key=lambda x: x["score"], reverse=True)

        self.results = normalized[: self.k]

        return self

import asyncio
import logging
from dataclasses import dataclass
from typing import Any

from packages.features.vector_index.pipeline.builder import PipelineBuilder

logger = logging.getLogger("packages.features.vector_index.engine")


# ==========================================================
# PIPELINE DEPS
# ==========================================================


@dataclass
class PipelineDeps:
    vector_store: Any
    embedding_fn: Any
    memory_provider: Any
    entity_provider: Any
    context_provider: Any
    ann: Any

    temporal_index: Any | None = None
    causal_graph: Any | None = None
    cluster_router: Any | None = None
    importance: Any | None = None


# ==========================================================
# ENGINE
# ==========================================================


class VectorIndex:
    def __init__(
        self,
        components: Any,
        embedding_service: Any,
        tokenizer: Any,
        memory_provider: Any = None,
        entity_provider: Any = None,
        context_provider: Any = None,
        semantic_cache: Any = None,
        campaign_id: str | None = None,
    ) -> None:
        self.components = components

        self.embedding_service = embedding_service
        self.tokenizer = tokenizer

        self.vector_store = components.vector_reader

        self.memory_provider = memory_provider
        self.entity_provider = entity_provider
        self.context_provider = context_provider

        self._pipeline: Any = None
        self._pipeline_lock = asyncio.Lock()

        self._fallback_ann: Any = None
        self._ann: Any = None

        self.semantic_cache = semantic_cache
        self.campaign_id = campaign_id

    @property
    def is_ready(self) -> bool:
        """
        Verifica se todas as tarefas de inicialização em background foram concluídas.
        """
        tasks = getattr(self.components, "_background_tasks", [])
        return all(t.done() for t in tasks) if tasks else True

    # ==========================================================
    # EMBEDDING (SAFE WRAPPER)
    # ==========================================================

    async def _embed(self, text: str) -> list[float]:
        """
        Garante que a geração de embeddings não bloqueie o event loop,
        delegando para o executor se for uma operação síncrona ou CPU-bound.
        """
        result: list[float] = await self.components.executor.run(self.embedding_service.embed, text)
        return result

    # ==========================================================
    # ANN RESOLUTION (CACHED)
    # ==========================================================

    def _get_ann(self) -> Any:
        # Se o índice ANN estiver pronto, usamos o caminho rápido
        ann = getattr(self.components, "ann", None)
        if ann:
            return ann

        ivf = getattr(self.components, "ivf_router", None)
        # Verificamos se o ivf existe e se a inicialização já terminou
        if ivf and self.is_ready:
            return ivf

        if self._fallback_ann:
            return self._fallback_ann

        if hasattr(self.vector_store, "search"):
            status = "initializing" if not self.is_ready else "not configured"
            logger.warning(f"ANN {status} — using vector_store.search (slow path)")

            class VectorStoreANN:
                def __init__(self, store: Any) -> None:
                    self.store = store

                async def search(self, query_vector: list[float], k: int = 10) -> list[str]:
                    result: list[str] = await self.store.search(query_vector, k)
                    return result

            self._fallback_ann = VectorStoreANN(self.vector_store)
            return self._fallback_ann

        logger.error("No ANN or fallback available")
        return None

    def _resolve_ann(self) -> Any:
        if self._ann is None:
            self._ann = self._get_ann()
        return self._ann

    # ==========================================================
    # CONTEXT BUILDER
    # ==========================================================

    def _build_context(self, query: str, k: int) -> SearchContext:
        tokens = self.tokenizer.tokenize(query)

        if not isinstance(tokens, list):
            tokens = [tokens]

        return SearchContext(
            query=query,
            q_vec=None,
            query_tokens=tokens,
            query_type=None,
            vector_store=self.vector_store,
            k=k,
            token_store=self.components.token_store,
            metadata_store=self.components.metadata_store,
            ann=self._resolve_ann(),
            temporal_index=getattr(self.components, "temporal_index", None),
        )

    # ==========================================================
    # PIPELINE (THREAD-SAFE LAZY INIT)
    # ==========================================================

    async def _ensure_pipeline(self) -> Any:
        if self._pipeline is not None:
            return self._pipeline

        async with self._pipeline_lock:
            if self._pipeline is not None:
                return self._pipeline

            logger.info("Initializing retrieval pipeline")

            deps = PipelineDeps(
                vector_store=self.vector_store,
                embedding_fn=self._embed,
                memory_provider=self.memory_provider,
                entity_provider=self.entity_provider,
                context_provider=self.context_provider,
                ann=self._resolve_ann(),
                temporal_index=getattr(self.components, "temporal_index", None),
                causal_graph=getattr(self.components, "causal_graph", None),
                cluster_router=getattr(self.components, "cluster_router", None),
                importance=getattr(self.components, "importance", None),
            )

            self._pipeline = PipelineBuilder(deps).build()

            logger.info("Pipeline ready")

            return self._pipeline

    # ==========================================================
    # SEARCH DEBUG
    # ==========================================================

    async def search_debug(self, query: str, k: int = 4) -> dict[str, Any]:
        if not query:
            return {
                "results": [],
                "query": query,
                "tokens": [],
            }

        logger.debug("search_debug query_len=%s k=%s", len(query), k)

        pipeline = await self._ensure_pipeline()

        if pipeline is None:
            logger.error("Pipeline not available")
            return {"results": [], "query": query, "tokens": []}

        ctx = self._build_context(query, k)
        ctx = await pipeline.run(ctx)

        return {
            "results": ctx.results or [],
            "candidates": getattr(ctx, "candidates", []),
            "query": query,
            "tokens": ctx.query_tokens,
        }

    # ==========================================================
    # SEARCH FINAL
    # ==========================================================

    async def search_async(self, query: str, k: int = 4) -> list[Any]:
        if not query:
            return []

        logger.debug("search query_len=%s k=%s", len(query), k)

        try:
            # -----------------------------------------------------
            # EMBEDDING (necessário para semantic cache)
            # -----------------------------------------------------
            query_vector = await self._embed(query)

            # -----------------------------------------------------
            # 🔥 SEMANTIC CACHE (READ)
            # -----------------------------------------------------
            if self.semantic_cache and self.campaign_id:
                cached = await self.semantic_cache.get(
                    self.campaign_id,
                    query,
                    query_vector,
                )
                if cached is not None:
                    logger.debug("[VectorIndex] semantic cache hit")
                    return list(cached)

            # -----------------------------------------------------
            # PIPELINE
            # -----------------------------------------------------
            pipeline = await self._ensure_pipeline()

            if pipeline is None:
                logger.error("Pipeline not available")
                return []

            ctx = self._build_context(query, k)
            ctx.q_vec = query_vector

            ctx = await pipeline.run(ctx)

            results = ctx.results or []

            # -----------------------------------------------------
            # 🔥 SEMANTIC CACHE (WRITE)
            # -----------------------------------------------------
            if self.semantic_cache and self.campaign_id:
                try:
                    await self.semantic_cache.set(
                        self.campaign_id,
                        query,
                        query_vector,
                        results,
                    )
                except Exception:
                    logger.debug("semantic cache write failed")

            return results

        except TimeoutError:
            logger.warning("search timeout query_len=%s", len(query))
            return []

        except Exception:
            logger.exception("search failed query_len=%s", len(query))
            return []

    async def search(
        self,
        query: str,
        k: int = 4,
        q_vec: list[float] | None = None,
        top_k: int | None = None,
    ) -> list[Any]:
        """
        Search interface for compatibility.
        Accepts q_vec (pre-computed embedding) for optimization but doesn't use it.
        top_k is used if k is not provided.
        """
        actual_k = top_k if top_k is not None else k
        return await self.search_async(query, k=actual_k)
