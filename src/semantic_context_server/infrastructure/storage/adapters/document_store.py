from collections.abc import Mapping
from typing import Any

from semantic_context_server.application.ports.executor import ExecutorPort
from semantic_context_server.application.ports.storage import DocumentStorePort
from semantic_context_server.infrastructure.storage.base.base_kv_adapter import BaseKVAdapter


class DocumentStoreAdapter(BaseKVAdapter, DocumentStorePort):
    """
    Adapter semântico para documentos.
    """

    def __init__(self, kv_store: Any, executor: ExecutorPort) -> None:
        super().__init__(kv_store, executor)

    # ---------------------------------------------------------
    # WRITE
    # ---------------------------------------------------------
    async def set(self, key: str, value: Mapping[str, Any]) -> None:
        if not key:
            raise ValueError("doc_id cannot be empty")

        if not isinstance(value, dict):
            raise TypeError("document must be a dict")

        await super().set(key, value)

    # ---------------------------------------------------------
    # READ
    # ---------------------------------------------------------
    async def get(self, key: str) -> dict | None:
        if not key:
            return None

        result = await super().get(key)

        if result is None:
            return None

        if not isinstance(result, dict):
            raise TypeError("stored document must be a dict")

        return result
