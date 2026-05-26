import argparse
import asyncio
from typing import Any

from packages.features.benchmark_engine.application.run_benchmark_usecase import (
    RunBenchmarkInput,
)
from semantic_context_server.bootstrap.container import Container


class BenchmarkCLI:
    def __init__(self) -> None:
        container: Any = Container()
        self.usecase = container.run_benchmark

    def run(self) -> None:
        parser = argparse.ArgumentParser(description="RPG Benchmark CLI")

        parser.add_argument("--n", type=int, default=50)
        parser.add_argument("--mode", choices=["io", "cpu", "jitter"], default="io")

        parser.add_argument("--no-dedup", action="store_true")
        parser.add_argument("--batch", action="store_true")

        parser.add_argument("--workers", type=int, default=None)
        parser.add_argument("--cpu-work", type=int, default=2_000_000)

        args = parser.parse_args()

        asyncio.run(self._execute(args))

    async def _execute(self, args: Any) -> None:
        input_data = RunBenchmarkInput(
            mode=args.mode,
            n=args.n,
            batch=args.batch,
            cpu_work=args.cpu_work,
            workers=args.workers,
            dedup=not args.no_dedup,
        )

        result = await self.usecase.execute(input_data)

        self._print_report(result)

    def _print_report(self, report: dict) -> None:
        print("\n--- BENCHMARK REPORT ---")

        for k, v in report.items():
            if isinstance(v, float):
                print(f"{k}: {v:.4f}")
            else:
                print(f"{k}: {v}")
