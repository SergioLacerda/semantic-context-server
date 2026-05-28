from __future__ import annotations

from types import SimpleNamespace
from typing import Any

import pytest

from packages.core.bootstrap_runtime import EventBusPort, InProcessAsyncBus, ServiceGraph
from packages.interfaces.http_api import assembler as assembler_mod
from packages.interfaces.http_api.assembler import NarrativeServerAssembler
from semantic_context_server.application.ports.executor import ExecutorPort
from semantic_context_server.application.runtime.app_runtime import AppRuntime
from semantic_context_server.shared.cache.cache import CacheManager


class _FakeExecutor:
    async def shutdown(self) -> None:  # pragma: no cover
        return None


class _FakeContainer:
    def __init__(self, calls: list[str]) -> None:
        self._calls = calls
        self._executor = _FakeExecutor()

    def resolve(self, port: type[Any]) -> Any:
        if port is ExecutorPort:
            return self._executor
        raise KeyError(port)

    async def shutdown(self) -> None:
        self._calls.append("container_shutdown")


class _FakeCampaignManager:
    async def get(self, campaign_id: str) -> Any:
        _ = campaign_id
        return SimpleNamespace()

    async def shutdown(self) -> None:  # pragma: no cover
        return None


class _FakeBuilder:
    def __init__(self, calls: list[str]) -> None:
        self._calls = calls

    def build_tuple(self) -> tuple[_FakeContainer, _FakeCampaignManager]:
        self._calls.append("build_tuple")
        return _FakeContainer(self._calls), _FakeCampaignManager()


def test_assembler_registers_expected_ports(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[str] = []

    monkeypatch.setattr(assembler_mod, "ContainerBuilder", lambda: _FakeBuilder(calls))

    graph = ServiceGraph()
    assembler = NarrativeServerAssembler()
    assembler.assemble(graph)

    assert calls == ["build_tuple"]
    assert graph.has(AppRuntime)
    assert graph.has(CacheManager)
    assert graph.has(ExecutorPort)
    assert graph.has(EventBusPort)
    assert graph.has(InProcessAsyncBus)


def test_preflight_check_raises_on_invalid_config(monkeypatch: pytest.MonkeyPatch) -> None:
    def _boom() -> None:
        raise RuntimeError("invalid")

    monkeypatch.setattr(assembler_mod, "load_settings", _boom)

    assembler = NarrativeServerAssembler()
    checks = assembler.preflight_checks()
    assert len(checks) == 1

    with pytest.raises(RuntimeError):
        import asyncio

        asyncio.run(checks[0].check())


@pytest.mark.asyncio
async def test_shutdown_hooks_reverse_order_executes_bus_before_runtime(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[str] = []

    monkeypatch.setattr(assembler_mod, "ContainerBuilder", lambda: _FakeBuilder(calls))

    assembler = NarrativeServerAssembler()
    graph = ServiceGraph()
    assembler.assemble(graph)

    original_bus_shutdown = assembler._async_bus.shutdown

    async def _bus_shutdown_probe() -> None:
        calls.append("bus_shutdown")
        await original_bus_shutdown()

    assembler._async_bus.shutdown = _bus_shutdown_probe

    # LifecycleOrchestrator executes hooks in reverse order; emulate here.
    hooks = assembler.shutdown_hooks()
    for hook in reversed(hooks):
        await hook.fn()

    assert calls == ["build_tuple", "bus_shutdown", "container_shutdown"]
