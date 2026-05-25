import asyncio
import time
from typing import Any

from semantic_context_server.infrastructure.adapters.benchmark.engine_factory import (
    IndexProtocol,
    RetrievalLike,
)
from semantic_context_server.infrastructure.adapters.benchmark.metrics import build_report


async def run_concurrent(
    engine: RetrievalLike,
    index: IndexProtocol,
    n: int = 50,
    same_query: bool = True,
) -> Any:
    async def call(i: int) -> float:
        query = "same" if same_query else f"q{i}"

        start = time.perf_counter()
        await engine.search(query)
        return time.perf_counter() - start

    start_total = time.perf_counter()

    latencies = await asyncio.gather(*[call(i) for i in range(n)])

    total = time.perf_counter() - start_total

    return build_report(latencies, total, index.calls)


async def run_sequential(
    engine: RetrievalLike,
    index: IndexProtocol,
    n: int = 50,
    same_query: bool = True,
) -> Any:
    latencies = []

    start_total = time.perf_counter()

    for i in range(n):
        query = "same" if same_query else f"q{i}"

        start = time.perf_counter()
        await engine.search(query)
        latencies.append(time.perf_counter() - start)

    total = time.perf_counter() - start_total

    return build_report(latencies, total, index.calls)
