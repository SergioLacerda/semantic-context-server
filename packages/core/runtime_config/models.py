import logging
from dataclasses import dataclass

from packages.core.runtime_config.types import Environment, ProfileName, StorageType


@dataclass(frozen=True)
class LLMSettings:
    provider: str
    model: str
    api_key: str | None = None
    base_url: str | None = None
    timeout: int = 180


@dataclass(frozen=True)
class EmbeddingSettings:
    provider: str
    model: str
    api_key: str | None = None
    base_url: str | None = None
    batch_size: int = 32
    dimension: int = 768
    timeout: int = 180


@dataclass(frozen=True)
class RuntimeSettings:
    environment: Environment
    profile: ProfileName
    device: str | None = None
    log_level: int = logging.INFO
    execution_timeout: int = 180
    max_cache_size: int = 10000
    executor_task_timeout: int = 300


@dataclass(frozen=True)
class ModelSettings:
    delegate: str = "external"


@dataclass(frozen=True)
class ExternalModelSettings:
    base_url: str = ""
    api_key: str | None = None
    timeout: int = 180


@dataclass(frozen=True)
class LocalModelSettings:
    name: str = "gpt2"
    device: str | None = None


@dataclass(frozen=True)
class CompressionSettings:
    level: int = 3


@dataclass(frozen=True)
class LRUSettings:
    max_items: int = 10000
    ttl_seconds: int = 1800


@dataclass(frozen=True)
class DiskSettings:
    base_path: str = ".analysis/cache"
    ttl_seconds: int = 86400


@dataclass(frozen=True)
class CacheSettings:
    lru: LRUSettings = LRUSettings()
    disk: DiskSettings = DiskSettings()
    compression: CompressionSettings = CompressionSettings()


@dataclass(frozen=True)
class AppSettings:
    campaign_file: str
    storage: StorageType = "json"
    rotation_size: int = 1024
    max_entries_per_file: int = 5000
    max_campaigns: int = 100
    campaign_ttl: int = 3600
    campaign_cleanup_interval: int = 60
    world: str = "default"
    discord_enable: bool = False
    discord_token: str | None = None
    discord_public_key: str | None = None
    discord_app_id: str | None = None


@dataclass(frozen=True)
class Settings:
    runtime: RuntimeSettings
    llm: LLMSettings
    embeddings: EmbeddingSettings
    app: AppSettings
    model: ModelSettings = ModelSettings()
    external_model: ExternalModelSettings = ExternalModelSettings()
    local_model: LocalModelSettings = LocalModelSettings()
    cache: CacheSettings = CacheSettings()


from types import SimpleNamespace as _NS  # noqa: E402

settings = _NS(
    cache=_NS(
        disk=_NS(base_path=".analysis/cache", ttl_seconds=86400),
        lru=_NS(max_items=10000, ttl_seconds=1800),
        compression=_NS(level=3),
    )
)
