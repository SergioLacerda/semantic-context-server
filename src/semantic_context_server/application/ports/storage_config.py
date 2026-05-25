from pathlib import Path
from typing import Protocol

from semantic_context_server.application.ports.storage_policy import StoragePolicy
from semantic_context_server.application.ports.storage_types import (
    StorageBackend,
    StorageKind,
)


class StorageConfigPort(Protocol):
    """
    Define como o sistema resolve:

    - backend por tipo de storage (kv, vector, etc)
    - policy por tipo
    - path base por campanha
    """

    # ======================================================
    # PATH
    # ======================================================

    def get_base_path(self, campaign_id: str) -> Path: ...

    # ======================================================
    # BACKEND (WHAT → HOW)
    # ======================================================

    def get_backend(self, kind: StorageKind) -> StorageBackend: ...

    # ======================================================
    # POLICY (COMPORTAMENTO)
    # ======================================================

    def get_policy(self, kind: StorageKind) -> StoragePolicy: ...
