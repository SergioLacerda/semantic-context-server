from dataclasses import dataclass

from packages.core.runtime_config.loader import AppSettings


@dataclass(frozen=True)
class StorageConfig:
    storage: str
    campaign_file: str
    rotation_size: int
    max_entries_per_file: int


def from_runtime(settings: AppSettings) -> StorageConfig:
    return StorageConfig(
        storage=settings.storage,
        campaign_file=settings.campaign_file,
        rotation_size=settings.rotation_size,
        max_entries_per_file=settings.max_entries_per_file,
    )
