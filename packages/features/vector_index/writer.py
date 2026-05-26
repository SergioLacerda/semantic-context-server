import asyncio
import contextlib
import inspect
import logging
import time
from concurrent.futures import Executor
from typing import Any

from packages.features.vector_index.contracts import VectorWriterPort
from packages.core.shared_kernel.hash_utils import sha256_hash

logger = logging.getLogger(__name__)

_SENTINEL: object = object()


class VectorWriterService(VectorWriterPort):
    def __init__(
        self,
        vector_index: Any,
        embedding_cache: Any = None,
        batch_size: int = 8,
        flush_interval: float = 1.0,
        max_queue_size: int = 1000,
        max_retries: int = 3,
        shutdown_timeout: float = 5.0,
        executor: Executor | None = None,
        managed: bool = False,
    ) -> None:
        if not managed:
            raise RuntimeError("VectorWriterService must be created via container (managed=True)")

        # unwrap adapter
        engine = vector_index
        while hasattr(engine, "raw"):
            engine = engine.raw

        self.vector_store = engine.vector_store
        self.embedding_service = engine.embedding_service
        self.document_store = engine.components.document_store
        self.metadata_store = engine.components.metadata_store

        self.embedding_cache = embedding_cache

        self.batch_size = batch_size
        self.flush_interval = flush_interval
        self.max_retries = max_retries
        self.shutdown_timeout = shutdown_timeout
        self.executor = executor

        self._queue: asyncio.Queue[Any] = asyncio.Queue(maxsize=max_queue_size)
        self._worker_task: asyncio.Task[None] | None = None
        self._started = False

        # metrics
        self._processed = 0
        self._failed = 0
        self._dropped = 0

    # ==========================================================
    # LIFECYCLE
    # ==========================================================

    async def start(self) -> None:
        if self._started:
            return

        if self._worker_task and not self._worker_task.done():
            raise RuntimeError("VectorWriterService already running")

        logger.debug("Starting VectorWriterService")

        self._worker_task = asyncio.create_task(self._worker_loop())
        self._started = True

    async def shutdown(self) -> None:
        if not self._started:
            return

        logger.debug("Shutting down VectorWriterService")
        self._started = False

        # envia sentinel
        try:
            self._queue.put_nowait(_SENTINEL)
        except asyncio.QueueFull:
            with contextlib.suppress(Exception):
                self._queue.get_nowait()
            with contextlib.suppress(Exception):
                self._queue.put_nowait(_SENTINEL)

        if self._worker_task:
            try:
                await asyncio.wait_for(
                    asyncio.shield(self._worker_task),
                    timeout=self.shutdown_timeout,
                )
            except TimeoutError:
                logger.warning("Worker shutdown timeout — forcing cancel")

        if self._worker_task and not self._worker_task.done():
            self._worker_task.cancel()
            with contextlib.suppress(Exception):
                await self._worker_task

        await self._drain_queue()
        self._worker_task = None

    def _ensure_started(self) -> None:
        if not self._started or (self._worker_task and self._worker_task.done()):
            self._started = False
            raise RuntimeError("VectorWriterService has not been started")

    # ==========================================================
    # PUBLIC API
    # ==========================================================

    async def flush(self) -> None:
        """
        Força o processamento imediato de todos os itens na fila.
        Útil para tornar testes determinísticos e garantir persistência.
        """
        if self._queue.empty():
            return

        items: list[Any] = []
        while not self._queue.empty():
            try:
                item = self._queue.get_nowait()
                if item is _SENTINEL:
                    # Devolve o sentinel para não quebrar o loop do worker
                    await self._queue.put(item)
                    break
                items.append(item)
            except asyncio.QueueEmpty:
                break

        if items:
            logger.debug("Manual flush triggering for %d items", len(items))
            await self._flush_with_retry(items)

    async def store_event(
        self, campaign_id: str, texts: list[str], metadata: dict[str, Any]
    ) -> None:
        await self.store_events(campaign_id, texts, metadata)

    async def upsert(
        self,
        campaign_id: str,
        texts: list[str],
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Alias para store_events alinhado com nomenclatura moderna de storage."""
        await self.store_events(campaign_id, texts, metadata)

    async def store_events(
        self,
        campaign_id: str,
        texts: list[str],
        metadata: dict[str, Any] | None = None,
    ) -> None:
        self._ensure_started()

        if not texts:
            return

        metadata = metadata or {}
        dropped = 0

        for text in texts:
            if not text or not text.strip():
                continue

            # Filter out short texts (less than 2 characters)
            if len(text.strip()) < 2:
                continue

            item = {
                "id": self._generate_id(campaign_id, text),
                "text": text.strip(),
                "metadata": {
                    **metadata,
                    "campaign_id": campaign_id,
                },
            }

            if not self._put_nowait_force(item):
                dropped += 1

        if dropped:
            self._dropped += dropped
            logger.warning("Queue full — dropped %s events", dropped)

    # ==========================================================
    # WORKER
    # ==========================================================

    async def _worker_loop(self) -> None:
        buffer: list[Any] = []
        last_flush = time.time()
        try:
            while True:
                sentinel_seen = await self._fill_buffer(buffer)
                if sentinel_seen:
                    break
                if self._should_flush(buffer, last_flush):
                    await self._flush_with_retry(buffer)
                    buffer.clear()
                    last_flush = time.time()
        except Exception:
            logger.exception("Worker crashed")

        if buffer:
            try:
                await self._flush_with_retry(buffer)
            except Exception:
                logger.exception("Final flush failed")

    async def _fill_buffer(self, buffer: list[Any]) -> bool:
        try:
            item = await asyncio.wait_for(self._queue.get(), timeout=self.flush_interval)
        except TimeoutError:
            if buffer:
                await self._flush_with_retry(buffer)
                buffer.clear()
            return False

        if item is _SENTINEL:
            return True

        buffer.append(item)
        self._drain_greedy(buffer)
        return False

    def _drain_greedy(self, buffer: list[Any]) -> None:
        while len(buffer) < self.batch_size:
            try:
                nxt = self._queue.get_nowait()
                if nxt is _SENTINEL:
                    self._queue.put_nowait(nxt)
                    break
                buffer.append(nxt)
            except asyncio.QueueEmpty:
                break

    def _should_flush(self, buffer: list[Any], last_flush: float) -> bool:
        return len(buffer) >= self.batch_size or (time.time() - last_flush) >= self.flush_interval

    # ==========================================================
    # BACKPRESSURE
    # ==========================================================

    def _put_nowait_force(self, item: Any) -> bool:
        try:
            self._queue.put_nowait(item)
            return True
        except asyncio.QueueFull:
            with contextlib.suppress(Exception):
                self._queue.get_nowait()
            try:
                self._queue.put_nowait(item)
                return True
            except Exception:
                return False

    # ==========================================================
    # FLUSH
    # ==========================================================

    async def _flush_with_retry(self, batch: list[Any]) -> None:
        for attempt in range(self.max_retries):
            try:
                await self._flush(batch)
                self._processed += len(batch)
                return
            except Exception:
                self._failed += len(batch)
                logger.exception("Flush failed (%s)", attempt + 1)
                await asyncio.sleep(0.1 * (attempt + 1))

        self._dropped += len(batch)

    async def _flush(self, batch: list[Any]) -> None:
        texts = [e["text"] for e in batch]
        embeddings = await self._embed_batch(texts)

        # Operação agora é puramente assíncrona para compor com VectorBatchWriter
        await self._storage_write_async(batch, embeddings)

    # ==========================================================
    # STORAGE (ASYNC)
    # ==========================================================

    async def _storage_write_async(self, batch: list[Any], embeddings: list[Any]) -> None:
        for i, event in enumerate(batch):
            doc_id = event["id"]

            # Deduplicação respeitando o Async Mandate
            if await self.document_store.get(doc_id):
                continue

            # VectorBatchWriter.add está sendo testado com MockVectorStore que é sync
            # Tentamos awaitar caso seja async, caso contrário chamamos diretamente
            add_result = self.vector_store.add(doc_id, embeddings[i])
            if inspect.iscoroutine(add_result) or isinstance(add_result, asyncio.Future):
                await add_result

            await self.document_store.set(doc_id, {"text": event["text"]})
            await self.metadata_store.set(doc_id, event["metadata"])

    # ==========================================================
    # EMBEDDING
    # ==========================================================

    async def _embed_batch(self, texts: list[str]) -> list[Any]:
        if self.embedding_cache:
            try:
                cached: list[Any] = await self.embedding_cache.get_many(texts)
                return cached
            except Exception:
                pass

        # Check if embed_batch is available
        if getattr(self.embedding_service, "supports_batch", False):
            batched: list[Any] = await self.embedding_service.embed_batch(texts)
            return batched

        # Check if embed is async or sync
        embed_func = self.embedding_service.embed
        if inspect.iscoroutinefunction(embed_func):
            # Async embed method
            return list(await asyncio.gather(*(embed_func(t) for t in texts)))
        else:
            # Sync embed method - call directly without await
            return [embed_func(t) for t in texts]

    # ==========================================================
    # UTILS
    # ==========================================================

    async def _drain_queue(self) -> None:
        while not self._queue.empty():
            try:
                self._queue.get_nowait()
            except Exception:
                break

    def _generate_id(self, campaign_id: str, text: str) -> str:
        h = sha256_hash({"campaign_id": campaign_id, "text": text})
        return f"{campaign_id}:{h}"
