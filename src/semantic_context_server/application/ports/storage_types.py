from typing import Literal

# ==========================================================
# TYPES
# ==========================================================

StorageKind = Literal["kv", "vector", "document", "metadata"]
StorageBackend = Literal["json", "chroma", "inmemory"]


# ==========================================================
# CONSTANTS
# ==========================================================


class StorageKinds:
    KV: StorageKind = "kv"
    VECTOR: StorageKind = "vector"
    DOCUMENT: StorageKind = "document"
    METADATA: StorageKind = "metadata"


class StorageBackends:
    JSON: StorageBackend = "json"
    CHROMA: StorageBackend = "chroma"
    MEMORY: StorageBackend = "inmemory"
