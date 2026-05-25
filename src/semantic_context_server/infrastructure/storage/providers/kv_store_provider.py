from typing import Any

from semantic_context_server.application.ports.executor import ExecutorPort
from semantic_context_server.application.ports.storage_types import StorageKinds
from semantic_context_server.infrastructure.storage.base.base_kv_adapter import BaseKVAdapter
from semantic_context_server.infrastructure.storage.kv.in_memory_kv_store import InMemoryKVStore
from semantic_context_server.infrastructure.storage.kv.json_kv_store import JSONKeyValueStore
from semantic_context_server.infrastructure.storage.providers.storage_backend_registry import (
    get_global_registry,
)


class KVStoreProvider:
    def __init__(self, config: Any, executor: ExecutorPort) -> None:
        self.config = config
        self.executor = executor
        self._cache: dict[str, BaseKVAdapter] = {}

    def get(self, namespace: str) -> BaseKVAdapter:
        if namespace in self._cache:
            return self._cache[namespace]

        backend = self.config.get_backend(StorageKinds.KV)

        if backend == "inmemory":
            store = BaseKVAdapter(InMemoryKVStore(), self.executor)

        elif backend == "json":
            safe_namespace = namespace.replace(":", "_")
            base = self.config.get_base_path(safe_namespace)
            store = BaseKVAdapter(
                JSONKeyValueStore(base / f"{safe_namespace}.json", self.executor), self.executor
            )

        else:
            registry = get_global_registry()
            factory = registry.get(backend)
            res = factory(
                base_path=self.config.get_base_path(namespace),
                executor=self.executor,
                config=self.config,
                policy=self.config.get_policy(StorageKinds.KV),
            )
            storage_backend = res  # assume not awaitable for test backends

            if hasattr(storage_backend, "build_kv_store"):
                store = storage_backend.build_kv_store(namespace)
            else:
                raise ValueError(f"Unsupported KV backend: {backend}")

        self._cache[namespace] = store
        return store
