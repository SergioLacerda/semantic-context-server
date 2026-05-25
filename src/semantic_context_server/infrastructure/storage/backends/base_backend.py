from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from semantic_context_server.application.ports.executor import ExecutorPort
from semantic_context_server.infrastructure.storage.vector_store_config import VectorStoreConfig


class StorageBackendPlugin:
    name: str | None = None

    @classmethod
    def build(
        cls,
        base_path: Path | None,
        executor: ExecutorPort,
        config: VectorStoreConfig | None,
        policy: Any = None,
    ) -> "StorageBackend":
        raise NotImplementedError


class StorageBackend(ABC):
    @abstractmethod
    def build_vector_store(self) -> Any:
        raise NotImplementedError

    @abstractmethod
    def build_document_store(self) -> Any:
        raise NotImplementedError

    @abstractmethod
    def build_token_store(self) -> Any:
        raise NotImplementedError

    @abstractmethod
    def build_metadata_store(self) -> Any:
        raise NotImplementedError

    def _ensure_adapter(
        self, store: Any, expected_methods: list[str], name: str | None = None
    ) -> Any:
        label = name or "store"

        missing = [method for method in expected_methods if not hasattr(store, method)]

        if missing:
            raise TypeError(
                f"[{self.__class__.__name__}] {label} must implement methods "
                f"{missing}, got {type(store).__name__}"
            )

        return store
