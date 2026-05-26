import asyncio
import logging
from dataclasses import dataclass
from typing import Any

from semantic_context_server.application.ports.executor import ExecutorPort
from packages.features.vector_index.components import VectorWriter

logger = logging.getLogger(__name__)


@dataclass
class VectorTask:
    doc_id: str
    vector: list[float]
    metadata: dict[str, Any]


class VectorBatchWriter(VectorWriter):
    """
    Componente interno de infraestrutura para batching de escrita vetorial.
    ✔ Acumula documentos para reduzir I/O
    ✔ Flush automático por tempo ou tamanho
    ✔ Utilizado internamente pelo VectorIndex
    """

    def __init__(
        self,
        underlying_writer: VectorWriter,
        executor: ExecutorPort,
        batch_size: int = 10,
        flush_interval: float = 5.0,
    ):
        self._writer = underlying_writer
        self._executor = executor
        self._batch_size = batch_size
        self._flush_interval = flush_interval

        self._queue: list[VectorTask] = []
        self._lock = asyncio.Lock()
        self._flush_task: asyncio.Task[None] | None = None

    async def start(self) -> None:
        if self._flush_task is None:
            self._flush_task = asyncio.create_task(self._periodic_flush())

    async def stop(self) -> None:
        if self._flush_task:
            self._flush_task.cancel()
            await self.flush()

    async def add(self, doc_id: str, vector: list[float], metadata: dict[str, Any]) -> None:
        async with self._lock:
            self._queue.append(VectorTask(doc_id, vector, metadata))

            if len(self._queue) >= self._batch_size:
                # Agenda o flush para não bloquear a chamada atual
                asyncio.create_task(self.flush())

    async def clear(self) -> None:
        async with self._lock:
            self._queue.clear()
            await self._writer.clear()

    async def flush(self) -> None:
        async with self._lock:
            if not self._queue:
                return

            batch = list(self._queue)
            self._queue.clear()

            logger.debug("Flushing %d vectors to storage", len(batch))

            # Executa o batch de forma assíncrona.
            # O writer subjacente (ex: ChromaAdapter) gerenciará sua própria thread via Executor.
            tasks = [self._writer.add(t.doc_id, t.vector, t.metadata) for t in batch]
            await asyncio.gather(*tasks)

    async def _periodic_flush(self) -> None:
        while True:
            try:
                await asyncio.sleep(self._flush_interval)
                await self.flush()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("Error in VectorWriter periodic flush: %s", e)
