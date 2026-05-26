from __future__ import annotations

from typing import Any

from packages.features.benchmark_engine.contracts import BenchmarkRunnerContract


class BenchmarkEngineService:
    """Isolated benchmark capability service, decoupled from transactional flow."""

    def __init__(self, runner: BenchmarkRunnerContract) -> None:
        self._runner = runner

    async def run(self, mode: str = "io", n: int = 50, batch: bool = False, **kwargs: Any) -> dict[str, Any]:
        return await self._runner.run(mode=mode, n=n, batch=batch, **kwargs)
