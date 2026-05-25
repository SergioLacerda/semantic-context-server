from dataclasses import dataclass


@dataclass(frozen=True)
class StoragePolicy:
    """
    Define comportamento do storage (independente do backend).
    """

    enable_rotation: bool = False
    rotation_size: int = 1000

    compress: bool = False
    ttl_seconds: int | None = None
