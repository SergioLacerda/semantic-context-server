from pathlib import Path

from semantic_context_server.application.ports.storage_config import StorageConfigPort
from semantic_context_server.application.ports.storage_policy import StoragePolicy
from semantic_context_server.application.ports.storage_types import (
    StorageKinds,
)
from semantic_context_server.infrastructure.storage.providers.storage_backend_registry import (
    get_global_registry,
)


class FailingStorageConfig(StorageConfigPort):
    def __init__(self):
        self._backends = {
            StorageKinds.KV: "failing",
            StorageKinds.VECTOR: "failing",
            StorageKinds.DOCUMENT: "failing",
            StorageKinds.METADATA: "failing",
        }
        self._policies = {
            kind: StoragePolicy(enable_rotation=False, rotation_size=1024)
            for kind in self._backends
        }

        registry = get_global_registry()
        if "failing" not in registry.list():
            registry.register("failing", lambda *args, **kwargs: FailingStorageBackend())

    def get_backend(self, kind: str) -> str:
        return self._backends[kind]

    def get_policy(self, kind: str) -> StoragePolicy:
        return self._policies[kind]

    def get_base_path(self, campaign_id: str) -> Path:
        return Path("/tmp") / campaign_id


class _FailingKVStore:
    def set(self, *a, **k):
        raise RuntimeError("Storage failure")

    def get(self, *a, **k):
        raise RuntimeError("Storage failure")

    def clear(self):
        raise RuntimeError("Storage failure")


class _FailingVectorStore:
    def add(self, *a, **k):
        raise RuntimeError("Storage failure")

    def get(self, *a, **k):
        raise RuntimeError("Storage failure")

    def search(self, *a, **k):
        raise RuntimeError("Storage failure")

    def clear(self):
        raise RuntimeError("Storage failure")


# ---------------------------------------------------------
# backend
# ---------------------------------------------------------


class FailingStorageBackend:
    def __init__(self, *args, **kwargs):
        pass

    def build_kv_store(self, namespace: str):
        return _FailingKVStore()

    def build_document_store(self):
        return _FailingKVStore()

    def build_metadata_store(self):
        return _FailingKVStore()

    def build_token_store(self):
        return _FailingKVStore()

    def build_vector_store(self):
        return _FailingVectorStore()
