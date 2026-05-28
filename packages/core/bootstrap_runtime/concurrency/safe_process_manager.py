from __future__ import annotations

import asyncio
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from packages.core.bootstrap_runtime.concurrency.safe_executor import SafeExecutor


class BulkheadSaturatedError(RuntimeError):
    pass


@dataclass
class JobRecord:
    task: asyncio.Task[Any]
    owner_scope: str
    deadline: float | None
    domain: str


class SafeProcessManager:
    def __init__(self, executor: SafeExecutor, *, bulkhead_size: int = 8) -> None:
        self.executor = executor
        self.active_jobs: dict[str, JobRecord] = {}
        self.orphan_count = 0
        self._intake_open = True
        self._bulkheads = {
            "rpg": asyncio.Semaphore(bulkhead_size),
            "dev": asyncio.Semaphore(bulkhead_size),
            "indexing": asyncio.Semaphore(bulkhead_size),
        }

    async def dispatch(
        self,
        fn: Callable[..., Any],
        args: tuple[Any, ...],
        owner_scope: str,
        deadline: float,
        domain: str = "rpg",
    ) -> str:
        if not self._intake_open:
            raise RuntimeError("SafeProcessManager is shutting down")

        sem = self._bulkheads.setdefault(domain, asyncio.Semaphore(8))
        if sem.locked():
            raise BulkheadSaturatedError(f"Bulkhead saturated: {domain}")

        await sem.acquire()
        job_id = f"{owner_scope}:{len(self.active_jobs)+1}"

        async def _run() -> Any:
            try:
                return await asyncio.wait_for(self.executor.run(fn, *args), timeout=deadline)
            except TimeoutError:
                self.orphan_count += 1
                raise
            finally:
                sem.release()

        task = asyncio.create_task(_run())
        self.active_jobs[job_id] = JobRecord(
            task=task,
            owner_scope=owner_scope,
            deadline=deadline,
            domain=domain,
        )

        def _cleanup(_t: asyncio.Task[Any]) -> None:
            self.active_jobs.pop(job_id, None)

        task.add_done_callback(_cleanup)
        return job_id

    async def shutdown(self) -> None:
        self._intake_open = False
        for rec in list(self.active_jobs.values()):
            rec.task.cancel()
        if self.active_jobs:
            await asyncio.gather(*(r.task for r in self.active_jobs.values()), return_exceptions=True)
        self.active_jobs.clear()
