import random
from collections.abc import Callable
from typing import Any

from semantic_context_server.application.ports.executor import ExecutorPort


class FaultyExecutor(ExecutorPort):
    """
    Decorator para ExecutorPort que permite injeção de falhas controladas.
    Útil para testar resiliência no VectorIndexBuilder.
    """

    def __init__(self, real_executor: ExecutorPort):
        self._real = real_executor
        self._fail_targets: dict[str, float] = {}  # fn_name -> probability

    def set_fault(self, fn_name: str, probability: float = 1.0):
        self._fail_targets[fn_name] = probability

    async def start(self):
        await self._real.start()

    async def shutdown(self):
        await self._real.shutdown()

    async def run(self, fn: Callable[..., Any], *args, **kwargs):
        fn_name = fn.__name__ if hasattr(fn, "__name__") else str(fn)

        if fn_name in self._fail_targets:
            if random.random() <= self._fail_targets[fn_name]:
                raise RuntimeError(f"[FAULT INJECTION] Simulated failure in {fn_name}")

        return await self._real.run(fn, *args, **kwargs)

    async def run_async(self, fn, *args, **kwargs):
        return await self.run(fn, *args, **kwargs)
