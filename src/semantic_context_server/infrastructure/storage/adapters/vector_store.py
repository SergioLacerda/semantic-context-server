from typing import Any

from semantic_context_server.application.ports.executor import ExecutorPort
from semantic_context_server.infrastructure.storage.base.base_vector_adapter import (
    BaseVectorAdapter,
)


class VectorStoreAdapter(BaseVectorAdapter):
    def __init__(self, store: Any, executor: ExecutorPort) -> None:
        super().__init__(store, executor)
