import asyncio
from types import SimpleNamespace
from typing import Any, cast
from unittest.mock import MagicMock

import pytest

from semantic_context_server.interfaces.cli.benchmark_cli import BenchmarkCLI


class MockUseCase:
    def __init__(self):
        self.called_with: Any | None = None

    async def execute(self, input_data):
        self.called_with = input_data
        return {
            "p95": 10.1234,
            "avg": 5.5678,
            "throughput": 100,
        }


@pytest.mark.asyncio
async def test_execute_builds_input_and_calls_usecase(monkeypatch):
    # Evita KeyError ao instanciar BenchmarkCLI que tenta resolver run_benchmark
    monkeypatch.setattr(
        "semantic_context_server.bootstrap.container.Container.run_benchmark", MagicMock()
    )

    cli = BenchmarkCLI()

    mock_usecase = MockUseCase()
    cli.usecase = cast(Any, mock_usecase)

    printed = []

    monkeypatch.setattr(cli, "_print_report", lambda r: printed.append(r))

    args = SimpleNamespace(
        mode="cpu",
        n=10,
        batch=True,
        cpu_work=123,
        workers=4,
        no_dedup=False,
    )

    await cli._execute(args)

    assert mock_usecase.called_with is not None

    assert mock_usecase.called_with.mode == "cpu"
    assert mock_usecase.called_with.n == 10
    assert mock_usecase.called_with.batch is True
    assert mock_usecase.called_with.cpu_work == 123
    assert mock_usecase.called_with.workers == 4
    assert mock_usecase.called_with.dedup is True

    assert len(printed) == 1


def test_print_report_formats_output(capsys, monkeypatch):
    # Evita KeyError ao instanciar BenchmarkCLI
    monkeypatch.setattr(
        "semantic_context_server.bootstrap.container.Container.run_benchmark", MagicMock()
    )

    cli = BenchmarkCLI()

    report = {
        "p95": 10.1234,
        "avg": 5.5678,
        "throughput": 100,
    }

    cli._print_report(report)

    captured = capsys.readouterr()

    assert "--- BENCHMARK REPORT ---" in captured.out
    assert "p95: 10.1234" in captured.out
    assert "avg: 5.5678" in captured.out
    assert "throughput: 100" in captured.out


def test_run_invokes_asyncio(monkeypatch):
    # Evita KeyError ao instanciar BenchmarkCLI
    monkeypatch.setattr(
        "semantic_context_server.bootstrap.container.Container.run_benchmark", MagicMock()
    )

    cli = BenchmarkCLI()

    called = {"ok": False}

    async def fake_execute(args):
        called["ok"] = True

    monkeypatch.setattr(cli, "_execute", fake_execute)

    class FakeParser:
        def add_argument(self, *a, **k):
            pass

        def parse_args(self):
            return SimpleNamespace(
                mode="io",
                n=50,
                batch=False,
                cpu_work=1,
                workers=None,
                no_dedup=False,
            )

    monkeypatch.setattr("argparse.ArgumentParser", lambda **k: FakeParser())

    def fake_run(coro):
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(coro)
        finally:
            loop.close()

    monkeypatch.setattr("asyncio.run", fake_run)

    cli.run()

    assert called["ok"] is True
