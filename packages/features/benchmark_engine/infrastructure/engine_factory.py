import asyncio
import os
import random
from collections.abc import Iterable
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from enum import Enum
from functools import partial
from typing import Any, Protocol

from packages.features.benchmark_engine.infrastructure.retrieval_adapter import (
    RetrievalAdapter,
)


class ExecutorType(str, Enum):
    THREAD = "thread"
    PROCESS = "process"


class Executor:
    def __init__(self, mode: ExecutorType, max_workers: int | None = None) -> None:
        self.mode = mode
        self.max_workers = max_workers
        self._pool = (
            ProcessPoolExecutor(max_workers=max_workers)
            if mode == ExecutorType.PROCESS
            else ThreadPoolExecutor(max_workers=max_workers)
        )

    async def run(self, fn: Any, *args: Any) -> Any:
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(self._pool, partial(fn, *args))

# ==================================================
# PROTOCOL (contrato mínimo)
# ==================================================


class RetrievalLike(Protocol):
    async def search(self, query: str) -> Any: ...


class IndexProtocol(Protocol):
    calls: int

    async def search(self, query: Any, q_vec: Any, k: int) -> Any: ...


# ==================================================
# CPU WORK
# ==================================================


def cpu_heavy_compute(work: int) -> int:
    total = 0
    for i in range(work):
        total += i * i
    return total


# ==================================================
# INDEXES (simulações)
# ==================================================


class SlowIndex:
    def __init__(self, delay: float = 0.05) -> None:
        self.delay = delay
        self.calls = 0

    async def search(self, query: Any, q_vec: Any, k: int) -> list[Any]:
        self.calls += 1
        await asyncio.sleep(self.delay)
        return [query]


class JitterIndex:
    def __init__(self, min_delay: float = 0.03, max_delay: float = 0.1) -> None:
        self.min = min_delay
        self.max = max_delay
        self.calls = 0

    async def search(self, query: Any, q_vec: Any, k: int) -> list[Any]:
        self.calls += 1
        await asyncio.sleep(random.uniform(self.min, self.max))
        return [query]


class CpuBoundIndex:
    def __init__(self, work: int = 2_000_000) -> None:
        self.work = work
        self.calls = 0

    async def search(self, query: Any, q_vec: Any, k: int) -> list[Any]:
        self.calls += 1
        cpu_heavy_compute(self.work)
        return [query]


# ==================================================
# EMBEDDINGS (fake)
# ==================================================


class FakeEmbedding:
    async def get(self, query: Any) -> list[float]:
        return [1.0]

    async def embed(self, query: Any) -> list[float]:
        return [1.0]


class BatchEmbedding:
    def __init__(self) -> None:
        self.calls = 0

    async def embed_batch(self, texts: Iterable[str]) -> list[list[float]]:
        self.calls += 1
        await asyncio.sleep(0.01)
        return [[1.0] for _ in texts]

    async def get(self, text: Any) -> list[float]:
        return [1.0]

    async def embed(self, text: Any) -> list[float]:
        return [1.0]


# ==================================================
# CACHE (fake)
# ==================================================


class FakeSemanticCache:
    def __init__(self) -> None:
        self.store: dict[Any, Any] = {}

    async def get(self, query: Any, vec: Any) -> Any:
        return self.store.get(query)

    async def set(self, query: Any, vec: Any, value: Any) -> None:
        self.store[query] = value


class LocalRetrievalEngine:
    """Benchmark-local retrieval engine to avoid deep cross-feature coupling."""

    def __init__(
        self,
        *,
        vector_index: IndexProtocol,
        embedding_service: Any,
        embedding_cache: Any,
        semantic_cache: Any,
        executor: Any,
        enable_hedging: bool = True,
    ) -> None:
        self.vector_index = vector_index
        self.embedding_service = embedding_service

    async def search(self, query: str) -> Any:
        q_vec = await self.embedding_service.get(query)
        return await self.vector_index.search(query, q_vec, 5)


# ==================================================
# FACTORY
# ==================================================


def create_engine(
    mode: str = "io",
    batch: bool = False,
    cpu_work: int = 2_000_000,
    workers: int | None = None,
) -> tuple[RetrievalLike, IndexProtocol]:
    index: IndexProtocol
    if mode == "cpu":
        index = CpuBoundIndex(work=cpu_work)

        cpu_count = os.cpu_count() or 1
        workers = workers or max(2, cpu_count // 2)

        executor = Executor(mode=ExecutorType.PROCESS, max_workers=workers)

    elif mode == "jitter":
        index = JitterIndex()
        executor = Executor(mode=ExecutorType.THREAD, max_workers=workers)

    else:
        index = SlowIndex()
        executor = Executor(mode=ExecutorType.THREAD, max_workers=workers)

    embedding: Any = BatchEmbedding() if batch else FakeEmbedding()

    engine = LocalRetrievalEngine(
        vector_index=index,
        embedding_service=embedding,
        embedding_cache=embedding,
        semantic_cache=FakeSemanticCache(),
        executor=executor,
        enable_hedging=True,
    )

    adapter = RetrievalAdapter(engine)

    return adapter, index
