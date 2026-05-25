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
from semantic_context_server.infrastructure.storage.bootstrap import (
    ensure_memory_structure,
    ensure_storage_structure,
)
from semantic_context_server.infrastructure.storage.kv.json_kv_store import JSONKeyValueStore
from semantic_context_server.infrastructure.storage.vector.json_vector_store import JSONVectorStore
from semantic_context_server.infrastructure.storage.vector_store_config import VectorStoreConfig


class JSONStorageBackend(StorageBackend):
    """
    Backend baseado em arquivos JSON.
    """

    def __init__(
        self,
        base_path: Path,
        executor: ExecutorPort,
        config: VectorStoreConfig | None = None,
    ) -> None:
        self.base = base_path
        self.executor = executor
        self._ensure_base()
        self.config = config or VectorStoreConfig()

    def _ensure_base(self) -> None:
        ensure_storage_structure(self.base)
        ensure_memory_structure(self.base)

    def _kv(self, name: str) -> JSONKeyValueStore:
        return JSONKeyValueStore(self.base / f"{name}.json", self.executor)

    def build_kv_store(self, namespace: str) -> JSONKeyValueStore:
        return JSONKeyValueStore(self.base / "kv" / f"{namespace}.json", self.executor)

    def build_vector_store(self) -> Any:
        store = VectorStoreAdapter(
            JSONVectorStore(self.base / "vectors.json", self.config), self.executor
        )

        return self._ensure_adapter(store, ["add", "get", "search", "clear"], "vector_store")

    def build_document_store(self) -> Any:
        store = DocumentStoreAdapter(self._kv("documents"), self.executor)

        return self._ensure_adapter(store, ["get", "set", "clear"], "document_store")

    def build_token_store(self) -> Any:
        return TokenStoreAdapter(self._kv("tokens"), self.executor)

    def build_metadata_store(self) -> Any:
        return MetadataStoreAdapter(self._kv("metadata"), self.executor)


class JSONStorageBackendPlugin(StorageBackendPlugin):
    name = "json"

    @classmethod
    def build(
        cls,
        base_path: Path | None,
        executor: ExecutorPort,
        config: VectorStoreConfig | None,
        policy: Any = None,
    ) -> JSONStorageBackend:
        if base_path is None:
            raise ValueError("base_path is required for JSONStorageBackend")
        return JSONStorageBackend(base_path, executor, config)
