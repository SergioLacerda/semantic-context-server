from collections.abc import Callable
from typing import Any

from semantic_context_server.application.ports.storage_types import StorageBackend


class StorageBackendRegistry:
    """
    Registry de backends de storage (plugin system).

    ✔ type-safe (StorageBackend)
    ✔ singleton global
    ✔ compatível com DI
    """

    def __init__(self) -> None:
        self._backends: dict[StorageBackend, Callable[..., Any]] = {}

    # ---------------------------------------------------------
    # REGISTER
    # ---------------------------------------------------------

    def register(self, name: StorageBackend, backend: Callable[..., Any]) -> None:
        if name in self._backends:
            return

        self._backends[name] = backend

    # ---------------------------------------------------------
    # RESOLVE
    # ---------------------------------------------------------

    def get(self, name: StorageBackend) -> Callable[..., Any]:
        if name not in self._backends:
            raise ValueError(
                f"Backend '{name}' not registered. Available: {list(self._backends.keys())}"
            )

        return self._backends[name]

    # ---------------------------------------------------------
    # INFO
    # ---------------------------------------------------------

    def list(self) -> list[StorageBackend]:
        return list(self._backends.keys())


# ==========================================================
# 🔥 SINGLETON GLOBAL
# ==========================================================

_global_registry: StorageBackendRegistry | None = None


def get_global_registry() -> StorageBackendRegistry:
    global _global_registry

    if _global_registry is None:
        _global_registry = StorageBackendRegistry()

    return _global_registry
