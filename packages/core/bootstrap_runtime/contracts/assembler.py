from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from packages.core.bootstrap_runtime.contracts.service_graph import ServiceGraph


@dataclass(frozen=True)
class PreflightCheck:
    name: str
    check: Callable[[], Awaitable[None]]


@dataclass(frozen=True)
class WarmupHook:
    name: str
    fn: Callable[[], Awaitable[None]]


@dataclass(frozen=True)
class ShutdownHook:
    name: str
    fn: Callable[[], Awaitable[None]]


@runtime_checkable
class AssemblerPort(Protocol):
    def assemble(self, graph: ServiceGraph) -> None: ...
    def preflight_checks(self) -> list[PreflightCheck]: ...
    def warmup_hooks(self) -> list[WarmupHook]: ...
    def shutdown_hooks(self) -> list[ShutdownHook]: ...
