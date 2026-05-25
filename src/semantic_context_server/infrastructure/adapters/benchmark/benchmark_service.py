from typing import Any

from semantic_context_server.infrastructure.adapters.benchmark.engine_factory import (
    create_engine,
)
from semantic_context_server.infrastructure.adapters.benchmark.scenarios import (
    run_concurrent,
    run_sequential,
)


class BenchmarkService:
    async def run(
        self,
        mode: str = "io",
        n: int = 50,
        batch: bool = False,
        cpu_work: int = 2_000_000,
        workers: int | None = None,
        dedup: bool = True,
        strategy: str = "concurrent",
    ) -> Any:
        engine, index = create_engine(
            mode=mode,
            batch=batch,
            cpu_work=cpu_work,
            workers=workers,
        )

        if strategy == "sequential":
            return await run_sequential(
                engine,
                index,
                n=n,
                same_query=dedup,
            )

        return await run_concurrent(
            engine,
            index,
            n=n,
            same_query=dedup,
        )
