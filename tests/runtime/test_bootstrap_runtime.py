import asyncio

import pytest

from packages.core.bootstrap_runtime import (
    AssemblerPort,
    DuplicateRegistrationError,
    LifecycleOrchestrator,
    PreflightCheck,
    ServiceGraph,
    ShutdownHook,
    UnregisteredPortError,
    WarmupHook,
)
from packages.core.bootstrap_runtime.runtime_scope import RuntimeScopeManager


class _DummyAssembler(AssemblerPort):
    def __init__(self, *, preflight_error: bool = False, warmup_error: bool = False) -> None:
        self.preflight_error = preflight_error
        self.warmup_error = warmup_error
        self.shutdown_called = False

    def assemble(self, graph: ServiceGraph) -> None:
        graph.register(str, "ok")

    def preflight_checks(self) -> list[PreflightCheck]:
        async def _check() -> None:
            if self.preflight_error:
                raise RuntimeError("preflight")

        return [PreflightCheck(name="check", check=_check)]

    def warmup_hooks(self) -> list[WarmupHook]:
        async def _hook() -> None:
            if self.warmup_error:
                raise RuntimeError("warmup")

        return [WarmupHook(name="warmup", fn=_hook)]

    def shutdown_hooks(self) -> list[ShutdownHook]:
        async def _shutdown() -> None:
            self.shutdown_called = True

        return [ShutdownHook(name="shutdown", fn=_shutdown)]


def test_service_graph_register_resolve_and_duplicate_guard() -> None:
    graph = ServiceGraph()
    instance = object()

    graph.register(str, instance)
    assert graph.resolve(str) is instance
    assert graph.has(str)

    # Idempotent re-register with same instance
    graph.register(str, instance)

    with pytest.raises(DuplicateRegistrationError):
        graph.register(str, object())

    with pytest.raises(UnregisteredPortError):
        graph.resolve(int)


@pytest.mark.asyncio
async def test_lifecycle_orchestrator_start_and_shutdown() -> None:
    assembler = _DummyAssembler()
    orchestrator = LifecycleOrchestrator(assembler)

    graph = await orchestrator.start()
    assert orchestrator.ready() is True
    assert graph.resolve(str) == "ok"

    await orchestrator.shutdown("test")
    assert orchestrator.ready() is False
    assert assembler.shutdown_called is True


@pytest.mark.asyncio
async def test_lifecycle_orchestrator_collects_warmup_errors_non_fatal() -> None:
    assembler = _DummyAssembler(warmup_error=True)
    orchestrator = LifecycleOrchestrator(assembler)

    await orchestrator.start()
    assert orchestrator.ready() is True
    assert len(orchestrator.warmup_errors) == 1


@pytest.mark.asyncio
async def test_runtime_scope_manager_ttl_and_lru_eviction() -> None:
    class _Runtime:
        def __init__(self) -> None:
            self.shutdown_called = False

        async def shutdown(self) -> None:
            self.shutdown_called = True

    class _Builder:
        async def build_scope_runtime(self, world_id: str, scope_id: str) -> _Runtime:
            _ = (world_id, scope_id)
            return _Runtime()

    manager = RuntimeScopeManager(_Builder(), max_size=1, ttl_seconds=0)

    first = await manager.get("rpg", "scope-a")
    await asyncio.sleep(0)
    _second = await manager.get("rpg", "scope-b")

    # max_size=1 forces eviction of least recently used (first)
    assert first.shutdown_called is True

    await manager.shutdown()
