from collections.abc import Awaitable, Callable
from typing import Any, TypeVar

T = TypeVar("T")


class _RegistryProxy:
    """Proxy that allows forced override of registrations (used in tests)."""

    def __init__(self, data: dict[type, Any]) -> None:
        self._data = data

    def register(self, port: type, instance: Any) -> None:
        self._data[port] = instance


class Container:
    """
    Container simples, tipado por Ports.
    Sem service locator implícito.
    """

    settings: Any | None = None
    run_benchmark: Any | None = None

    def __init__(self) -> None:
        self._data: dict[type, Any] = {}
        self._registry = _RegistryProxy(self._data)
        # Dynamic slots — populated by ContainerBuilder
        self.application_registry: Any | None = None
        self.campaigns: Any | None = None
        self.command_bus: Any | None = None
        self.event_bus: Any | None = None
        self.llm: Any | None = None
        self.embedding: Any | None = None
        self.start: Callable[[], Awaitable[None]] | None = None
        self.shutdown: Callable[[], Awaitable[None]] | None = None
        # Set by test factories for lifecycle assertions
        self._lifecycle_guard: Any | None = None
        self._default_campaign: Any | None = None
        # Legacy attributes used by CLI/API tests.
        self.settings: Any | None = None
        self.run_benchmark: Any | None = None

    def register(self, port: type, instance: Any) -> None:
        if port in self._data and self._data[port] is not instance:
            raise ValueError(
                f"Dependency port already registered: {port}. "
                "Use the same instance or resolve the conflict explicitly."
            )
        self._data[port] = instance

    def resolve(self, port: type) -> Any:
        if port not in self._data:
            raise KeyError(f"Dependency not registered: {port}")
        return self._data[port]

    @property
    def interaction_state(self) -> Any:
        from semantic_context_server.application.ports.interaction_runtime import (
            InteractionRuntimePort,
        )

        return self._data.get(InteractionRuntimePort)

    def __getattr__(self, name: str) -> Any:
        campaign = self._default_campaign
        if campaign is not None and hasattr(campaign, name):
            return getattr(campaign, name)
        raise AttributeError(f"{type(self).__name__!r} object has no attribute {name!r}")
