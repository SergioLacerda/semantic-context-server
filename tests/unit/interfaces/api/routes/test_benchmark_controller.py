from types import SimpleNamespace

import pytest

from semantic_context_server.application.dto.benchmark_request import BenchmarkRequest
from semantic_context_server.interfaces.api.routes.benchmark_controller import (
    compare,
    compare_strategies,
    run_benchmark,
)

# ==========================================================
# MOCKS
# ==========================================================


class MockUseCase:
    async def execute(self, input_data):
        return {"result": "run", "input": input_data.mode}

    async def compare(self, input_data):
        return {"result": "compare", "modes": input_data.n}

    async def compare_strategies(self, strategies):
        return {"result": "strategies", "count": len(strategies)}

    def generate_strategies(self):
        return ["s1", "s2"]


def build_request():
    mock_usecase = MockUseCase()

    container = SimpleNamespace(run_benchmark=mock_usecase)
    app = SimpleNamespace(state=SimpleNamespace(container=container))

    request = SimpleNamespace(app=app)

    return request


# ==========================================================
# TESTS
# ==========================================================


@pytest.mark.asyncio
async def test_run_benchmark():
    request = build_request()

    req = BenchmarkRequest(
        mode="cpu",
        n=10,
        batch=False,
        cpu_work=1,
        workers=None,
        dedup=True,
    )

    usecase = request.app.state.container.run_benchmark

    result = await run_benchmark(req, usecase)

    assert result["result"] == "run"
    assert result["input"] == "cpu"


@pytest.mark.asyncio
async def test_compare():
    request = build_request()
    usecase = request.app.state.container.run_benchmark

    result = await compare(
        usecase,
        n=20,
        batch=True,
        strategy="sequential",
    )

    assert result["result"] == "compare"
    assert result["modes"] == 20


@pytest.mark.asyncio
async def test_compare_strategies():
    request = build_request()
    usecase = request.app.state.container.run_benchmark

    result = await compare_strategies(usecase)

    assert result["result"] == "strategies"
    assert result["count"] == 2
