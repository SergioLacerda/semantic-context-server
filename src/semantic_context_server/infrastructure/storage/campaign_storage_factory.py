from pathlib import Path
from typing import Any

from semantic_context_server.application.ports.executor import ExecutorPort
from semantic_context_server.application.ports.storage_config import StorageConfigPort
from semantic_context_server.application.ports.storage_types import StorageKinds
from semantic_context_server.infrastructure.storage.providers.storage_backend_registry import (
    get_global_registry,
)

_registry = get_global_registry()


def build_campaign_storage(
    config: StorageConfigPort, campaign_id: str, executor: ExecutorPort
) -> Any:
    backend = config.get_backend(StorageKinds.KV)
    policy = config.get_policy(StorageKinds.KV)
    base_path = config.get_base_path(campaign_id)

    # ---------------------------------------------------------
    # 🔥 HARDENING (ESSENCIAL)
    # ---------------------------------------------------------

    if isinstance(base_path, str):
        base_path = Path(base_path)

    if not isinstance(base_path, Path):
        raise TypeError(f"Invalid base_path type: {type(base_path)}. Expected Path.")

    # ---------------------------------------------------------
    # factory
    # ---------------------------------------------------------

    factory = _registry.get(backend)

    if factory is None:
        raise ValueError(f"Unsupported storage type: {backend}")

    res = factory(base_path=base_path, executor=executor, config=config, policy=policy)
    return res  # assume not awaitable for test backends
