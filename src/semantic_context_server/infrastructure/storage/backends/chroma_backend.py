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
from semantic_context_server.infrastructure.storage.vector.chroma_vector_store import (
    ChromaVectorStore,
)
from semantic_context_server.infrastructure.storage.vector_store_config import VectorStoreConfig


class ChromaStorageBackend(StorageBackend):
    def __init__(self, executor: ExecutorPort, base_path: Path | None = None) -> None:
        self.base = base_path or Path("./data")
        self.base.mkdir(parents=True, exist_ok=True)
        self.executor = executor

        self.client = self._load_chroma_lib()

    def _load_chroma_lib(self) -> Any:
        try:
            import chromadb

            return chromadb.Client(
                chromadb.config.Settings(
                    persist_directory=str(self.base / "chroma"),
                    anonymized_telemetry=False,
                )
            )
        except ImportError as e:
            raise RuntimeError(
                "ChromaStorageBackend requires optional dependency 'chromadb'. "
                "Install with: pip install semantic_context_server[vector-db]"
            ) from e

    def _get_collection(self, name: str) -> Any:
        return self.client.get_or_create_collection(name=name)

    # ---------------------------------------------------------
    # STORES
    # ---------------------------------------------------------

    def build_vector_store(self) -> Any:
        collection = self._get_collection("vectors")
        store = VectorStoreAdapter(ChromaVectorStore(collection), self.executor)

        return self._ensure_adapter(store, ["add", "get", "search", "clear"], "chroma_vector_store")

    def build_document_store(self) -> Any:
        return DocumentStoreAdapter(InMemoryKVStore(), self.executor)

    def build_token_store(self) -> Any:
        return TokenStoreAdapter(InMemoryKVStore(), self.executor)

    def build_metadata_store(self) -> Any:
        return MetadataStoreAdapter(InMemoryKVStore(), self.executor)


class ChromaStorageBackendPlugin(StorageBackendPlugin):
    name = "chroma"

    @classmethod
    def build(
        cls,
        base_path: Path | None,
        executor: ExecutorPort,
        config: VectorStoreConfig | None,
        policy: Any = None,
    ) -> ChromaStorageBackend:
        return ChromaStorageBackend(executor, base_path)
