import asyncio
import inspect
from collections.abc import Callable
from typing import Any


class RetrievalEngine:
    """
    Infra de retrieval:

    ✔ cache (embedding + semantic)
    ✔ deduplicação inflight
    ✔ hedging opcional
    ✔ executor compatível
    ✔ thread-safe (async lock)
    """

    def __init__(
        self,
        vector_index: Any,
        embedding_cache: Any,
        semantic_cache: Any,
        embedding_service: Any = None,
        vector_index_factory: Callable[..., Any] | None = None,
        executor: Any = None,
        enable_hedging: bool = False,
        hedge_delay: float = 0.01,
    ) -> None:
        # Hard Guard: Se o index for uma corrotina, o sistema falhou ao fazer o await no container
        if inspect.iscoroutine(vector_index):
            raise TypeError(
                "RetrievalEngine received a coroutine as vector_index. "
                "Check if the StorageProvider.get() call is missing an 'await'."
            )

        # Padronização de unwrapping (mesmo padrão do VectorWriterService)
        engine = vector_index
        while hasattr(engine, "raw"):
            engine = engine.raw

        self.default_index = engine
        self.vector_index_factory = vector_index_factory

        # Prioriza o serviço injetado, com fallback para o índice (retrocompatibilidade)
        self.embedding_service = embedding_service or getattr(engine, "embedding_service", None)
        if not self.embedding_service:
            raise ValueError(
                "RetrievalEngine requires an embedding_service (either injected or via vector_index)"
            )

        self.embedding_cache = embedding_cache
        self.semantic_cache = semantic_cache
        self.executor = executor

        self.indexes: dict[Any, Any] = {}
        self._inflight: dict[Any, asyncio.Task[Any]] = {}
        self._lock = asyncio.Lock()

        self.enable_hedging = enable_hedging
        self.hedge_delay = hedge_delay

    # ---------------------------------------------------------
    # index
    # ---------------------------------------------------------

    async def _get_index(self, campaign_id: Any) -> Any:
        if campaign_id is None:
            return self.default_index

        if campaign_id in self.indexes:
            return self.indexes[campaign_id]

        if not self.vector_index_factory:
            return self.default_index

        res = self.vector_index_factory(campaign_id)
        index = await res if inspect.isawaitable(res) else res
        self.indexes[campaign_id] = index
        return index

    # ---------------------------------------------------------
    # embedding
    # ---------------------------------------------------------

    async def _get_embedding(self, query: str) -> Any:
        # 1. Tenta Cache
        if self.embedding_cache:
            cached = await self.embedding_cache.get(query)
            if cached:
                return cached

        # 2. Gera embedding
        service = self.embedding_service
        if service is None:
            raise RuntimeError("RetrievalEngine: embedding_service is not configured.")

        if self.executor:
            emb = await self.executor.run(service.embed, query)
        else:
            res = service.embed(query)
            emb = await res if inspect.isawaitable(res) else res

        # Garante que o embedding seja hashável (tupla) para compatibilidade com caches
        if isinstance(emb, list):
            emb = tuple(emb)

        # Opcional: Salvar no cache aqui se o service não o fizer
        return emb

    # ---------------------------------------------------------
    # execution
    # ---------------------------------------------------------

    async def _execute_index(self, index: Any, query: str, q_vec: Any, k: int) -> Any:
        if self.executor:
            # Garante que mesmo buscas síncronas rodem no pool global
            return await self.executor.run(index.search, query=query, q_vec=q_vec, k=k)

        res = index.search(query, q_vec, k)
        return await res if inspect.isawaitable(res) else res

    # ---------------------------------------------------------
    # hedging
    # ---------------------------------------------------------

    async def _hedged_search(self, index: Any, query: str, q_vec: Any, k: int) -> Any:
        async def primary() -> Any:
            return await self._execute_index(index, query, q_vec, k)

        async def secondary() -> Any:
            await asyncio.sleep(self.hedge_delay)
            return await self._execute_index(index, query, q_vec, k)

        tasks = [asyncio.create_task(primary()), asyncio.create_task(secondary())]
        try:
            return await self._first_success(tasks)
        finally:
            for t in tasks:
                if not t.done():
                    t.cancel()

    async def _first_success(self, tasks: list[asyncio.Task[Any]]) -> Any:
        remaining = list(tasks)
        while remaining:
            done, _ = await asyncio.wait(remaining, return_when=asyncio.FIRST_COMPLETED)
            for t in done:
                remaining.remove(t)
                try:
                    result = t.result()
                    for p in remaining:
                        p.cancel()
                    return result
                except Exception as e:
                    if not remaining:
                        raise e

    # ---------------------------------------------------------
    # search
    # ---------------------------------------------------------

    async def search(self, query: str, k: int = 4, campaign_id: Any = None) -> Any:
        index = await self._get_index(campaign_id)

        q_vec = await self._get_embedding(query)

        cached = await self.semantic_cache.get(query, q_vec)
        if cached:
            return cached

        inflight_key = (query, campaign_id, k)

        async with self._lock:
            if inflight_key in self._inflight:
                task = self._inflight[inflight_key]
            else:
                task = asyncio.create_task(self._execute(query, index, q_vec, k, inflight_key))
                self._inflight[inflight_key] = task

        return await task

    # ---------------------------------------------------------
    # execute wrapper
    # ---------------------------------------------------------

    async def _execute(
        self,
        query: str,
        index: Any,
        q_vec: Any,
        k: int,
        inflight_key: Any,
    ) -> Any:
        try:
            if self.enable_hedging:
                results = await self._hedged_search(index, query, q_vec, k)
            else:
                results = await self._execute_index(index, query, q_vec, k)

            await self.semantic_cache.set(query, q_vec, results)

            return results

        finally:
            async with self._lock:
                self._inflight.pop(inflight_key, None)
