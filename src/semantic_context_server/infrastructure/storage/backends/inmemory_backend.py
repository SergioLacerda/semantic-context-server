from pathlib import Path
from typing import Any

from semantic_context_server.application.ports.executor import ExecutorPort
from semantic_context_server.infrastructure.storage.adapters.document_store import (
    DocumentStoreAdapter,
)
from semantic_context_server.infrastructure.storage.adapters.metadata_store import (
    MetadataStoreAdapter,
)
from semantic_context_server.infrastructure.storage.adapters.token_store import TokenStoreAdapter
from semantic_context_server.infrastructure.storage.adapters.vector_store import VectorStoreAdapter
from semantic_context_server.infrastructure.storage.backends.base_backend import (
    StorageBackend,
    StorageBackendPlugin,
)
from semantic_context_server.infrastructure.storage.kv.in_memory_kv_store import InMemoryKVStore
from semantic_context_server.infrastructure.storage.vector_store_config import VectorStoreConfig


class InMemoryVectorStore:
    def __init__(self) -> None:
        self.data: dict[str, list[float]] = {}

    def add(
        self,
        doc_id: str,
        vector: list[float],
        metadata: dict[str, Any] | None = None,
    ) -> None:
        self.data[doc_id] = vector

    def get(self, doc_id: str) -> list[float] | None:
        return self.data.get(doc_id)

    def keys(self) -> list[str]:
        return list(self.data.keys())

    def search(self, vector: list[float], limit: int) -> list[str]:
        return list(self.data.keys())[:limit]

    def clear(self) -> None:
        self.data.clear()


class InMemoryStorageBackend(StorageBackend):
    def __init__(self, executor: ExecutorPort) -> None:
        self.executor = executor

    def build_vector_store(self) -> Any:
        store = VectorStoreAdapter(InMemoryVectorStore(), self.executor)
        return self._ensure_adapter(store, ["add", "get", "search", "clear"], "vector_store")

    def build_document_store(self) -> Any:
        store = DocumentStoreAdapter(InMemoryKVStore(), self.executor)
        return self._ensure_adapter(store, ["get", "set", "clear"], "document_store")

    def build_token_store(self) -> Any:
        return TokenStoreAdapter(InMemoryKVStore(), self.executor)

    def build_metadata_store(self) -> Any:
        return MetadataStoreAdapter(InMemoryKVStore(), self.executor)


class InMemoryStorageBackendPlugin(StorageBackendPlugin):
    name = "inmemory"

    @classmethod
    def build(
        cls,
        base_path: Path | None,
        executor: ExecutorPort,
        config: VectorStoreConfig | None,
        policy: Any = None,
    ) -> InMemoryStorageBackend:
        return InMemoryStorageBackend(executor)
