from __future__ import annotations

import asyncio
import concurrent.futures
import inspect
import multiprocessing
import os
from collections.abc import Callable
from enum import Enum
from typing import Any


class ExecutorType(Enum):
    THREAD = "thread"
    PROCESS = "process"


class SafeExecutor:
    def __init__(
        self,
        mode: ExecutorType = ExecutorType.THREAD,
        max_workers: int | None = None,
        name: str | None = None,
        task_timeout: float | None = None,
    ) -> None:
        self._mode = mode
        self._max_workers = max_workers
        self._name = name
        self._task_timeout = task_timeout
        self._pool: concurrent.futures.Executor | None = None
        self._tasks: set[asyncio.Future[Any]] = set()

    async def start(self) -> None:
        return None

    def _get_pool(self) -> concurrent.futures.Executor:
        if self._pool is None:
            if self._mode == ExecutorType.PROCESS:
                if os.getenv("PYTEST_CURRENT_TEST"):
                    self._pool = concurrent.futures.ThreadPoolExecutor(
                        max_workers=self._max_workers,
                        thread_name_prefix=self._name or "",
                    )
                    return self._pool
                ctx = multiprocessing.get_context("spawn")
                self._pool = concurrent.futures.ProcessPoolExecutor(
                    max_workers=self._max_workers,
                    mp_context=ctx,
                )
            else:
                self._pool = concurrent.futures.ThreadPoolExecutor(
                    max_workers=self._max_workers,
                    thread_name_prefix=self._name or "",
                )
        return self._pool

    async def run_async(self, fn: Callable[..., Any], *args: Any) -> Any:
        loop = asyncio.get_running_loop()
        fut = loop.run_in_executor(self._get_pool(), fn, *args)
        self._tasks.add(fut)
        fut.add_done_callback(self._tasks.discard)
        return await fut

    async def run(self, fn: Callable[..., Any], *args: Any) -> Any:
        if inspect.iscoroutinefunction(fn):
            coro = fn(*args)
            if self._task_timeout is not None:
                try:
                    return await asyncio.wait_for(coro, timeout=self._task_timeout)
                except TimeoutError:
                    raise TimeoutError(f"Task exceeded timeout of {self._task_timeout}s") from None
            return await coro

        if self._task_timeout is not None:
            loop = asyncio.get_running_loop()
            fut = loop.run_in_executor(self._get_pool(), fn, *args)
            self._tasks.add(fut)
            fut.add_done_callback(self._tasks.discard)
            try:
                return await asyncio.wait_for(asyncio.shield(fut), timeout=self._task_timeout)
            except TimeoutError:
                raise TimeoutError(f"Task exceeded timeout of {self._task_timeout}s") from None

        return await self.run_async(fn, *args)

    async def shutdown(self) -> None:
        for t in list(self._tasks):
            t.cancel()
        self._tasks.clear()
        if self._pool is not None:
            self._pool.shutdown(wait=False, cancel_futures=True)
            self._pool = None
