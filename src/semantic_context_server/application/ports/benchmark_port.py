from typing import Protocol


class BenchmarkPort(Protocol):
    async def run(
        self,
        mode: str,
        n: int,
        batch: bool,
        cpu_work: int = 2_000_000,
        workers: int | None = None,
        dedup: bool = True,
        strategy: str = "concurrent",
    ) -> dict: ...
