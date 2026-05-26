from typing import Any

from packages.features.benchmark_engine.infrastructure.engine_factory import (
    create_engine,
)
from packages.features.benchmark_engine.infrastructure.scenarios import (
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
