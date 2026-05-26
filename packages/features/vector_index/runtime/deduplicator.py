import asyncio
import contextlib
import logging
import time
from collections.abc import Callable, Coroutine
from typing import Any

from semantic_context_server.application.ports.executor import ExecutorPort

logger = logging.getLogger(__name__)


class InflightDeduplicator:
    """
    Evita execução duplicada de operações async.

    - deduplica chamadas concorrentes
    - mantém micro-cache com TTL
    - integra-se ao Executor para monitoramento e propagação de contexto
    """

    def __init__(self, executor: ExecutorPort, ttl: float = 2.0):
        self._inflight: dict[str, asyncio.Task] = {}
        self._recent: dict[str, tuple[float, Any]] = {}

        self._executor = executor
        self._ttl = ttl

    # ---------------------------------------------------------
    # execução deduplicada
    # ---------------------------------------------------------

    async def run(self, key: str, coro_factory: Callable[[], Coroutine[Any, Any, Any]]) -> Any:
        now = time.monotonic()

        # ---------------------------------------------------------
        # micro-cache
        # ---------------------------------------------------------

        if key in self._recent:
            ts, value = self._recent[key]

            if now - ts < self._ttl:
                return value

            del self._recent[key]

        # ---------------------------------------------------------
        # inflight dedup
        # ---------------------------------------------------------

        if key in self._inflight:
            return await self._inflight[key]

        # ---------------------------------------------------------
        # execução deduplicada (Async Task)
        # ---------------------------------------------------------
        # Criamos a tarefa diretamente. A delegação de processamento (threads/IO)
        # deve ser tratada dentro da factory (ex: EmbeddingService) utilizando
        # o executor injetado, mantendo a orquestração aqui puramente async.
        coro = coro_factory()
        task = asyncio.create_task(coro)

        self._inflight[key] = task

        try:
            result = await task

            self._recent[key] = (time.monotonic(), result)

            return result

        finally:
            self._inflight.pop(key, None)

    # ---------------------------------------------------------
    # ManagedComponent (Lifecycle)
    # ---------------------------------------------------------

    async def start(self) -> None:
        """Inicialização (satisfaz protocolo ManagedComponent)."""
        pass

    async def stop(self) -> None:
        """
        Interrompe execuções em voo durante o shutdown.
        """
        if not self._inflight:
            return

        logger.debug("Stopping InflightDeduplicator: cancelling %d tasks", len(self._inflight))
        for _key, task in list(self._inflight.items()):
            if not task.done():
                task.cancel()
                with contextlib.suppress(asyncio.CancelledError):
                    await task
        self.clear()

    # ---------------------------------------------------------
    # limpeza manual (opcional)
    # ---------------------------------------------------------

    def clear(self) -> None:
        self._inflight.clear()
        self._recent.clear()
