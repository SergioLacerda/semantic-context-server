from typing import Any

from fastapi import APIRouter, Depends, Query

from packages.features.benchmark_engine.application.run_benchmark_usecase import (
    CompareBenchmarkInput,
    RunBenchmarkInput,
)
from semantic_context_server.application.dto.benchmark_request import (
    BenchmarkRequest,
)
from semantic_context_server.interfaces.api.dependencies import get_container

router = APIRouter()


def get_usecase(container: Any = Depends(get_container)) -> Any:
    return container.run_benchmark


# ==========================================================
# RUN
# ==========================================================
@router.post("/benchmark/run")
async def run_benchmark(req: BenchmarkRequest, usecase: Any = Depends(get_usecase)) -> Any:
    input_data = RunBenchmarkInput(**req.model_dump())

    return await usecase.execute(input_data)


# ==========================================================
# COMPARE
# ==========================================================
@router.get("/benchmark/compare")
async def compare(
    usecase: Any = Depends(get_usecase),
    n: int = Query(50),
    batch: bool = Query(False),
    strategy: str = Query("concurrent"),
) -> Any:
    input_data = CompareBenchmarkInput(
        n=n,
        batch=batch,
        strategy=strategy,
    )

    return await usecase.compare(input_data)


# ==========================================================
# STRATEGIES
# ==========================================================
@router.get("/benchmark/strategies")
async def compare_strategies(usecase: Any = Depends(get_usecase)) -> Any:
    strategies = usecase.generate_strategies()

    return await usecase.compare_strategies(strategies)
