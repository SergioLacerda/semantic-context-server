from semantic_context_server.application.ports.storage_types import StorageBackends
from semantic_context_server.infrastructure.storage.backends.inmemory_backend import (
    InMemoryStorageBackendPlugin,
)
from semantic_context_server.infrastructure.storage.backends.json_backend import (
    JSONStorageBackendPlugin,
)
from semantic_context_server.infrastructure.storage.providers.storage_backend_registry import (
    StorageBackendRegistry,
    get_global_registry,
)


def create_storage_backend_registry() -> StorageBackendRegistry:
    registry = get_global_registry()

    if StorageBackends.MEMORY not in registry.list():
        registry.register(
            StorageBackends.MEMORY,
            InMemoryStorageBackendPlugin.build,
        )

    if StorageBackends.JSON not in registry.list():
        registry.register(
            StorageBackends.JSON,
            JSONStorageBackendPlugin.build,
        )

    return registry
