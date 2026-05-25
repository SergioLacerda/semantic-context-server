from pathlib import Path
from typing import Any, cast

from semantic_context_server.application.ports.storage_config import (
    StorageBackend,
    StorageConfigPort,
)
from semantic_context_server.application.ports.storage_policy import StoragePolicy


class SettingsStorageConfigAdapter(StorageConfigPort):
    def __init__(self, settings: Any) -> None:
        self.settings = settings

        # --------------------------------------------------
        # 🔥 BACKENDS POR TIPO
        # --------------------------------------------------
        self._backends: dict[str, StorageBackend] = self._load_backends()

        # --------------------------------------------------
        # 🔥 POLICY POR TIPO
        # --------------------------------------------------
        self._policies: dict[str, StoragePolicy] = self._load_policies()

    # =====================================================
    # BACKENDS
    # =====================================================

    def _load_backends(self) -> dict[str, StorageBackend]:
        """
        Suporta:
        - formato antigo (string)
        - formato novo (dict)
        """

        app = getattr(self.settings, "app", None)

        if app and hasattr(app, "storage_backends"):
            return cast(dict[str, StorageBackend], dict(app.storage_backends))

        storage = None

        if app and hasattr(app, "storage"):
            storage = app.storage
        elif hasattr(self.settings, "storage"):
            storage = self.settings.storage

        if isinstance(storage, str):
            backend = cast(StorageBackend, storage)
            return {
                "kv": backend,
                "vector": backend,
                "document": backend,
            }

        return {
            "kv": "inmemory",
            "vector": "inmemory",
            "document": "inmemory",
        }

    def get_backend(self, kind: str) -> StorageBackend:
        return self._backends.get(kind, "inmemory")

    # 🔙 compatibilidade
    def get_storage_type(self) -> StorageBackend:
        return self.get_backend("kv")

    # =====================================================
    # POLICY
    # =====================================================

    def _load_policies(self) -> dict[str, StoragePolicy]:
        """
        Permite policy global ou por tipo
        """

        default_policy = StoragePolicy(
            enable_rotation=getattr(self.settings, "enable_rotation", False),
            rotation_size=getattr(self.settings, "rotation_size", 1024),
        )

        app = getattr(self.settings, "app", None)

        # 🔥 NOVO formato (por tipo)
        if app and hasattr(app, "storage_policies"):
            raw = app.storage_policies

            policies = {}
            for kind, cfg in raw.items():
                policies[kind] = StoragePolicy(
                    enable_rotation=cfg.get("enable_rotation", default_policy.enable_rotation),
                    rotation_size=cfg.get("rotation_size", default_policy.rotation_size),
                )

            return policies

        return {
            "kv": default_policy,
            "vector": default_policy,
            "document": default_policy,
        }

    def get_policy(self, kind: str) -> StoragePolicy:
        return self._policies.get(kind, StoragePolicy())

    # =====================================================
    # PATH
    # =====================================================

    def get_base_path(self, campaign_id: str) -> Path:
        base = getattr(self.settings, "campaign_file", "./data")
        return Path(base) / campaign_id
