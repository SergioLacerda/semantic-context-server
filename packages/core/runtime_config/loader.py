import logging
import os
from functools import lru_cache

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from packages.core.runtime_config.env import load_environment
from packages.core.runtime_config.profile import get_profile_defaults
from packages.core.runtime_config.types import (
    EmbeddingProvider,
    Environment,
    LLMProvider,
    ProfileName,
    StorageType,
)

load_environment()


class RuntimeSettings(BaseModel):
    environment: Environment = Field(default="dev", alias="ENVIRONMENT")
    profile: ProfileName = Field(default="local", alias="APP_PROFILE")
    device: str | None = "cpu"
    log_level: int = logging.INFO
    execution_timeout: int = Field(default=180, alias="LLM_TIMEOUT")
    max_cache_size: int = Field(default=10000, alias="MAX_CACHE_SIZE")
    executor_task_timeout: int = Field(default=300, alias="EXECUTOR_TASK_TIMEOUT")


class LLMSettings(BaseModel):
    provider: LLMProvider = Field(default="openai", alias="LLM_PROVIDER")
    model: str = Field(default="gpt-4o", alias="LLM_MODEL")
    api_key: str | None = Field(default=None, alias="LLM_API_KEY")
    base_url: str | None = Field(default=None, alias="LLM_BASE_URL")
    timeout: int = 180


class EmbeddingSettings(BaseModel):
    provider: EmbeddingProvider = Field(default="openai", alias="EMBEDDING_PROVIDER")
    model: str = Field(default="text-embedding-3-small", alias="EMBEDDING_MODEL")
    api_key: str | None = Field(default=None, alias="EMBEDDING_API_KEY")
    base_url: str | None = Field(default=None, alias="EMBEDDING_BASE_URL")
    batch_size: int = Field(default=32, alias="EMBEDDING_BATCH_SIZE")
    dimension: int = Field(default=1536, alias="EMBEDDING_DIMENSION")
    timeout: int = Field(default=180, alias="EMBEDDING_TIMEOUT")


class AppSettings(BaseModel):
    campaign_file: str = Field(default="./data", alias="CAMPAIGN_PATH")
    storage: StorageType = Field(default="json", alias="STORAGE")
    rotation_size: int = Field(default=1024, alias="MAX_FILE_SIZE_KB")
    max_entries_per_file: int = Field(default=5000, alias="MAX_ENTRIES_PER_FILE")
    max_campaigns: int = Field(default=100, alias="MAX_CAMPAIGNS")
    campaign_ttl: int = Field(default=3600, alias="CAMPAIGN_TTL")
    campaign_cleanup_interval: int = Field(default=60, alias="CAMPAIGN_CLEANUP_INTERVAL")
    world: str = Field(default="default", alias="WORLD")
    discord_enable: bool = Field(default=False, alias="DISCORD_ENABLE")
    discord_token: str | None = Field(default=None, alias="DISCORD_TOKEN")
    discord_public_key: str | None = Field(default=None, alias="DISCORD_PUBLIC_KEY")
    discord_app_id: str | None = Field(default=None, alias="DISCORD_APPLICATION_ID")


class ModelSettings(BaseModel):
    delegate: str = Field(default="external", alias="MODEL_DELEGATE")


class Settings(BaseSettings):
    runtime: RuntimeSettings = Field(default_factory=RuntimeSettings)
    llm: LLMSettings = Field(default_factory=LLMSettings)
    embeddings: EmbeddingSettings = Field(default_factory=EmbeddingSettings)
    app: AppSettings = Field(default_factory=AppSettings)
    model: ModelSettings = Field(default_factory=ModelSettings)

    model_config = SettingsConfigDict(
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=False,
    )


def _apply_hardware_hacks(settings: Settings) -> None:
    if settings.runtime.device == "cpu":
        os.environ["CUDA_VISIBLE_DEVICES"] = ""


def _apply_profile_defaults(settings: Settings) -> None:
    get_profile_defaults(settings.runtime.profile)


@lru_cache
def load_settings() -> Settings:
    env_file = os.getenv("ENV_FILE", ".env")
    selected_env_file: str | None = env_file if env_file.lower() != "none" else None

    class _DynamicSettings(Settings):
        model_config = SettingsConfigDict(
            env_file=selected_env_file,
            env_file_encoding="utf-8",
            extra="ignore",
            populate_by_name=False,
        )

    settings: Settings = _DynamicSettings()
    _apply_profile_defaults(settings)
    _apply_hardware_hacks(settings)
    return settings
