import asyncio
import logging
from dataclasses import dataclass, field
from typing import Any

from packages.features.benchmark_engine.application.benchmark_strategy import BenchmarkStrategy
from packages.features.benchmark_engine.contracts import BenchmarkRunnerContract as BenchmarkPort
from packages.features.benchmark_engine.application.benchmark_analysis import (
    extract_winner,
    rank_strategies,
)

logger = logging.getLogger(__name__)


@dataclass
class RunBenchmarkInput:
    mode: str = "io"
    n: int = 50
    batch: bool = False
    cpu_work: int = 2_000_000
    workers: int | None = None
    dedup: bool = True
    strategy: str = "concurrent"


@dataclass
class CompareBenchmarkInput:
    modes: list[str] = field(default_factory=lambda: ["io", "jitter", "cpu"])
    n: int = 50
    batch: bool = False
    strategy: str = "concurrent"


class RunBenchmarkUseCase:
    def __init__(self, service: BenchmarkPort, executor: Any = None) -> None:
        self.service = service
        self.executor = executor

    async def execute(self, input_data: RunBenchmarkInput) -> dict[str, Any]:
        return await self.service.run(
            mode=input_data.mode,
            n=input_data.n,
            batch=input_data.batch,
            cpu_work=input_data.cpu_work,
            workers=input_data.workers,
            dedup=input_data.dedup,
            strategy=input_data.strategy,
        )

    async def compare(self, input_data: CompareBenchmarkInput) -> dict[str, Any]:
        async def run_mode(mode: str) -> tuple[str, dict[str, Any]]:
            try:
                result = await self.service.run(
                    mode=mode,
                    n=input_data.n,
                    batch=input_data.batch,
                    strategy=input_data.strategy,
                )
                return mode, result

            except Exception as e:
                logger.error("Benchmark mode %s failed: %s", mode, e)
                return mode, {
                    "error": str(e),
                    "status": "failed",
                }

        tasks = [run_mode(mode) for mode in input_data.modes]

        results = await asyncio.gather(*tasks)

        return {mode: result for mode, result in results}

    async def compare_strategies(
        self, strategies: list[BenchmarkStrategy], n: int = 50
    ) -> dict[str, Any]:
        async def run(strategy: BenchmarkStrategy) -> tuple[str, dict[str, Any]]:
            try:
                result = await self.service.run(
                    mode=strategy.mode,
                    n=n,
                    batch=strategy.batch,
                    workers=strategy.workers,
                    dedup=strategy.dedup,
                    strategy=strategy.strategy,
                )
                return strategy.name, result

            except Exception as e:
                logger.error("Benchmark strategy %s failed: %s", strategy.name, e)
                return strategy.name, {
                    "error": str(e),
                    "status": "failed",
                }

        tasks = [run(s) for s in strategies]

        results_list = await asyncio.gather(*tasks)

        results = {name: result for name, result in results_list}

        if self.executor:
            ranking = await self.executor.run(rank_strategies, results)
            winner = await self.executor.run(extract_winner, ranking)
        else:
            ranking = rank_strategies(results)
            winner = extract_winner(ranking)

        return {
            "results": results,
            "ranking": ranking,
            "winner": winner,
        }

    @staticmethod
    def generate_strategies() -> list[BenchmarkStrategy]:
        return [
            BenchmarkStrategy(name="baseline", batch=False, dedup=True),
            BenchmarkStrategy(name="no_dedup", batch=False, dedup=False),
            BenchmarkStrategy(name="batch_on", batch=True, dedup=True),
            BenchmarkStrategy(name="cpu_mode", mode="cpu"),
            BenchmarkStrategy(name="high_workers", workers=8),
        ]
