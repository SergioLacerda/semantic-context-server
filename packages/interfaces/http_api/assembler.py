from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from packages.core.bootstrap_runtime import (
    AssemblerPort,
    EventBusPort,
    InProcessAsyncBus,
    InProcessSyncBus,
    PreflightCheck,
    ServiceGraph,
    ShutdownHook,
    WarmupHook,
)
from packages.core.bootstrap_runtime.runtime_scope import RuntimeScopeManager
from packages.core.runtime_config.loader import load_settings
from packages.features.llm_gateway.contracts import LLMGatewayContract
from semantic_context_server.application.ports.event_bus import EventBus as LegacyEventBusPort
from semantic_context_server.application.ports.executor import ExecutorPort
from semantic_context_server.application.runtime.app_runtime import AppRuntime
from semantic_context_server.bootstrap.container_builder import ContainerBuilder
from semantic_context_server.shared.cache.cache import CacheManager


class _CampaignScopeAdapter:
    """Adapter that keeps AppRuntime campaign API while backed by RuntimeScopeManager."""

    def __init__(self, scope_manager: RuntimeScopeManager) -> None:
        self._scope_manager = scope_manager

    async def get(self, campaign_id: str) -> Any:
        return await self._scope_manager.get("rpg", f"campaign:{campaign_id}")

    async def clear(self, campaign_id: str) -> None:
        await self._scope_manager.clear("rpg", f"campaign:{campaign_id}")

    async def shutdown(self) -> None:
        await self._scope_manager.shutdown()


@dataclass
class NarrativeServerAssembler(AssemblerPort):
    _embedding_config: Any | None = None

    def __post_init__(self) -> None:
        self._container: Any | None = None
        self._scope_manager: RuntimeScopeManager | None = None
        self._sync_bus = InProcessSyncBus()
        self._async_bus = InProcessAsyncBus()

    def assemble(self, graph: ServiceGraph) -> None:
        builder = ContainerBuilder()
        container, scope_manager = builder.build_tuple()

        self._container = container
        self._scope_manager = scope_manager
        scope_adapter = _CampaignScopeAdapter(scope_manager)

        graph.register(type(container), container)
        graph.register(RuntimeScopeManager, scope_manager)
        graph.register(AppRuntime, AppRuntime(container, scope_adapter))
        graph.register(CacheManager, CacheManager())

        if hasattr(container, "resolve"):
            try:
                graph.register(ExecutorPort, container.resolve(ExecutorPort))
            except Exception:
                pass
            try:
                graph.register(LLMGatewayContract, container.resolve(LLMGatewayContract))
            except Exception:
                pass

        graph.register(EventBusPort, self._sync_bus)
        if hasattr(container, "resolve"):
            try:
                graph.register(LegacyEventBusPort, container.resolve(LegacyEventBusPort))
            except Exception:
                graph.register(LegacyEventBusPort, self._sync_bus)
        else:
            graph.register(LegacyEventBusPort, self._sync_bus)
        graph.register(InProcessAsyncBus, self._async_bus)

    def preflight_checks(self) -> list[PreflightCheck]:
        async def _config_check() -> None:
            load_settings()

        return [PreflightCheck(name="config", check=_config_check)]

    def warmup_hooks(self) -> list[WarmupHook]:
        return []

    def shutdown_hooks(self) -> list[ShutdownHook]:
        async def _shutdown_async_bus() -> None:
            await self._async_bus.shutdown()

        async def _shutdown_runtime() -> None:
            if self._container is not None and getattr(self._container, "shutdown", None):
                await self._container.shutdown()

        return [
            ShutdownHook(name="runtime_shutdown", fn=_shutdown_runtime),
            ShutdownHook(name="async_bus_shutdown", fn=_shutdown_async_bus),
        ]
