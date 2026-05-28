from __future__ import annotations

import asyncio
from typing import Any

from packages.core.bootstrap_runtime.contracts import AssemblerPort, ServiceGraph
from packages.core.bootstrap_runtime.telemetry import RuntimeTelemetry


class PreflightFailedError(RuntimeError):
    pass


class AssembleFailedError(RuntimeError):
    pass


class LifecycleOrchestrator:
    def __init__(self, assembler: AssemblerPort, config: Any = None) -> None:
        self.assembler = assembler
        self.config = config
        self.graph: ServiceGraph | None = None
        self._ready = False
        self.warmup_errors: list[Exception] = []
        self.telemetry = RuntimeTelemetry()

    async def start(self) -> ServiceGraph:
        with self.telemetry.phase_span("preflight"):
            for check in self.assembler.preflight_checks():
                try:
                    await check.check()
                except Exception as e:
                    raise PreflightFailedError(check.name) from e

        with self.telemetry.phase_span("assemble"):
            graph = ServiceGraph()
            try:
                self.assembler.assemble(graph)
            except Exception as e:
                raise AssembleFailedError("assemble") from e
            self.graph = graph

        with self.telemetry.phase_span("warmup"):
            hooks = self.assembler.warmup_hooks()
            if hooks:
                results = await asyncio.gather(*(h.fn() for h in hooks), return_exceptions=True)
                self.warmup_errors = [r for r in results if isinstance(r, Exception)]

        self._ready = True
        return self.graph

    def ready(self) -> bool:
        return self._ready

    async def shutdown(self, reason: str | None = None) -> None:
        del reason
        hooks = list(self.assembler.shutdown_hooks())
        for hook in reversed(hooks):
            try:
                await hook.fn()
            except Exception:
                continue
        self._ready = False
