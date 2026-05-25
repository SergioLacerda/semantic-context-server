import pytest

from semantic_context_server.application.dto.benchmark_strategy import (
    BenchmarkStrategy,
)
from semantic_context_server.usecases.run_benchmark import (
    CompareBenchmarkInput,
    RunBenchmarkInput,
    RunBenchmarkUseCase,
)

# ==========================================================
# MOCK SERVICE
# ==========================================================


class MockService:
    async def run(
        self,
        mode: str,
        n: int,
        batch: bool,
        cpu_work: int = 0,
        workers: int | None = None,
        dedup: bool = True,
        strategy: str = "default",
    ) -> dict:
        return {
            "p95": 10.0,
            "avg": 5.0,
            "throughput": 100.0,
        }


class ErrorService:
    async def run(
        self,
        mode: str,
        n: int,
        batch: bool,
        cpu_work: int = 0,
        workers: int | None = None,
        dedup: bool = True,
        strategy: str = "default",
    ) -> dict:
        raise RuntimeError("boom")


@pytest.mark.unit
@pytest.mark.asyncio
async def test_execute():
    usecase = RunBenchmarkUseCase(MockService())

    input_data = RunBenchmarkInput(mode="cpu")

    result = await usecase.execute(input_data)

    assert "p95" in result
    assert "avg" in result
    assert "throughput" in result


@pytest.mark.unit
@pytest.mark.asyncio
async def test_compare_success():
    usecase = RunBenchmarkUseCase(MockService())

    input_data = CompareBenchmarkInput(modes=["a", "b"])

    result = await usecase.compare(input_data)

    assert "a" in result
    assert "b" in result

    assert "p95" in result["a"]
    assert "avg" in result["a"]
    assert "throughput" in result["a"]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_compare_with_error():
    usecase = RunBenchmarkUseCase(ErrorService())

    input_data = CompareBenchmarkInput(modes=["x"])

    result = await usecase.compare(input_data)

    assert "x" in result
    assert result["x"]["status"] == "failed"
    assert "boom" in result["x"]["error"]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_compare_strategies_success():
    usecase = RunBenchmarkUseCase(MockService())

    strategies = [
        BenchmarkStrategy(name="s1"),
        BenchmarkStrategy(name="s2"),
    ]

    result = await usecase.compare_strategies(strategies)

    assert "results" in result
    assert "ranking" in result
    assert "winner" in result

    assert "s1" in result["results"]
    assert "s2" in result["results"]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_compare_strategies_with_error():
    usecase = RunBenchmarkUseCase(ErrorService())

    strategies = [BenchmarkStrategy(name="fail")]

    result = await usecase.compare_strategies(strategies)

    assert "fail" in result["results"]
    assert result["results"]["fail"]["status"] == "failed"


@pytest.mark.unit
def test_generate_strategies():
    strategies = RunBenchmarkUseCase.generate_strategies()

    names = [s.name for s in strategies]

    assert "baseline" in names
    assert "no_dedup" in names
    assert "batch_on" in names
