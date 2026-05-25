from pathlib import Path

from semantic_context_server.application.ports.storage_config import StorageConfigPort
from semantic_context_server.application.ports.storage_policy import StoragePolicy
from semantic_context_server.application.ports.storage_types import (
    StorageBackend,
    StorageBackends,
    StorageKind,
    StorageKinds,
)


class FakeStorageConfig(StorageConfigPort):
    """
    Fake limpo e alinhado com arquitetura FINAL.

    ✔ multi-backend por tipo
    ✔ policy por tipo
    ✔ multi-campaign via get_base_path
    ✔ sem compat legacy
    """

    def __init__(
        self,
        *,
        backends: dict[StorageKind, StorageBackend] | None = None,
        policies: dict[StorageKind, StoragePolicy] | None = None,
        namespace: str = "test",
        base_path: str | Path | None = None,
    ):
        default_backend = StorageBackends.MEMORY
        if backends is None and namespace in {
            StorageBackends.MEMORY,
            StorageBackends.JSON,
            "failing",
        }:
            default_backend = namespace

        self._backends: dict[StorageKind, StorageBackend] = backends or {
            StorageKinds.KV: default_backend,
            StorageKinds.VECTOR: default_backend,
            StorageKinds.DOCUMENT: default_backend,
            StorageKinds.METADATA: default_backend,
        }

        self._base_path = Path(base_path) if base_path is not None else None

        default_policy = StoragePolicy(
            enable_rotation=False,
            rotation_size=0,
        )

        self._policies: dict[StorageKind, StoragePolicy] = policies or {
            kind: default_policy for kind in self._backends
        }

        self.namespace = namespace

    # ======================================================
    # PORT IMPLEMENTATION
    # ======================================================

    def get_backend(self, kind: StorageKind) -> StorageBackend:
        if kind not in self._backends:
            raise ValueError(f"Backend not configured for kind: {kind}")
        return self._backends[kind]

    def get_policy(self, kind: StorageKind) -> StoragePolicy:
        if kind not in self._policies:
            raise ValueError(f"Policy not configured for kind: {kind}")
        return self._policies[kind]

    def get_base_path(self, campaign_id: str) -> Path:
        if self._base_path is not None:
            return self._base_path / campaign_id

        return Path(f"/tmp/{self.namespace}/{campaign_id}")

    # ======================================================
    # TEST HELPERS
    # ======================================================

    def override_backend(self, kind: StorageKind, backend: StorageBackend):
        self._backends[kind] = backend

    def override_policy(self, kind: StorageKind, policy: StoragePolicy):
        self._policies[kind] = policy
