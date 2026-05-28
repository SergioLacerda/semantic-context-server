from dataclasses import dataclass
from typing import cast

from packages.core.runtime_config.types import (
    EmbeddingProvider,
    Environment,
    LLMProvider,
    ProfileName,
    StorageType,
)

VALID_LLM_PROVIDERS: frozenset[str] = frozenset(
    {"openai", "lmstudio", "ollama", "groq", "anthropic"}
)
VALID_EMBEDDING_PROVIDERS: frozenset[str] = frozenset(
    {"openai", "sentence", "ollama", "lmstudio", "gemini"}
)
VALID_STORAGE: frozenset[str] = frozenset({"json", "chroma", "inmemory"})

DEFAULT_PROFILE = "local"


@dataclass(frozen=True)
class ProfileConfig:
    profile: ProfileName
    storage: StorageType
    campaign_file: str
    rotation_size: int
    max_entries_per_file: int
    llm_provider: LLMProvider
    llm_model: str
    llm_api_key: str | None
    llm_base_url: str | None
    llm_timeout: int
    embedding_provider: EmbeddingProvider
    embedding_model: str
    embedding_api_key: str | None
    embedding_base_url: str | None
    embedding_dim: int
    embedding_batch: int
    environment: Environment
    device: str | None
    log_level: int
    max_cache_size: int
    discord_enable: str | None
    discord_token: str | None
    discord_public_key: str | None
    discord_app_id: str | None
    max_campaigns: int = 100
    campaign_ttl: int = 3600
    campaign_cleanup_interval: int = 60
    world: str | None = None


_PROFILE_DEFAULTS: dict[str, dict[str, str | int]] = {
    "local": {
        "storage": "json",
        "llm_provider": "lmstudio",
        "llm_model": "local-model",
        "embedding_provider": "sentence",
        "embedding_model": "intfloat/e5-base-v2",
        "embedding_dim": 768,
    },
    "hybrid": {
        "storage": "chroma",
        "llm_provider": "openai",
        "llm_model": "gpt-4o-mini",
        "embedding_provider": "sentence",
        "embedding_model": "intfloat/e5-base-v2",
        "embedding_dim": 768,
    },
    "cloud": {
        "storage": "chroma",
        "llm_provider": "openai",
        "llm_model": "gpt-4o-mini",
        "embedding_provider": "openai",
        "embedding_model": "text-embedding-3-small",
        "embedding_dim": 1536,
    },
}


def get_profile_defaults(profile: str) -> dict[str, str | int]:
    if profile not in _PROFILE_DEFAULTS:
        raise ValueError(f"Invalid APP_PROFILE: {profile!r}. Valid: {sorted(_PROFILE_DEFAULTS)}")
    return _PROFILE_DEFAULTS[profile]


def build_profile(
    profile: str,
    storage: str,
    campaign_file: str,
    rotation_size: int,
    max_entries_per_file: int,
    llm_provider: str,
    llm_model: str,
    llm_api_key: str | None,
    llm_base_url: str | None,
    llm_timeout: int,
    embedding_provider: str,
    embedding_model: str,
    embedding_api_key: str | None,
    embedding_base_url: str | None,
    embedding_dim: int,
    embedding_batch: int,
    environment: str,
    device: str | None,
    log_level: int,
    max_cache_size: int,
    discord_enable: str | None,
    discord_token: str | None,
    discord_public_key: str | None,
    discord_app_id: str | None,
    max_campaigns: int,
    campaign_ttl: int,
    campaign_cleanup_interval: int,
    world: str | None,
) -> ProfileConfig:
    if llm_provider not in VALID_LLM_PROVIDERS:
        raise ValueError(
            f"Invalid LLM_PROVIDER: {llm_provider!r}. Valid: {sorted(VALID_LLM_PROVIDERS)}"
        )
    if embedding_provider not in VALID_EMBEDDING_PROVIDERS:
        raise ValueError(
            "Invalid EMBEDDING_PROVIDER: "
            f"{embedding_provider!r}. Valid: {sorted(VALID_EMBEDDING_PROVIDERS)}"
        )
    if storage not in VALID_STORAGE:
        raise ValueError(f"Invalid STORAGE: {storage!r}. Valid: {sorted(VALID_STORAGE)}")

    return ProfileConfig(
        profile=cast(ProfileName, profile),
        storage=cast(StorageType, storage),
        campaign_file=campaign_file,
        rotation_size=rotation_size,
        max_entries_per_file=max_entries_per_file,
        llm_provider=cast(LLMProvider, llm_provider),
        llm_model=llm_model,
        llm_api_key=llm_api_key,
        llm_base_url=llm_base_url,
        llm_timeout=llm_timeout,
        embedding_provider=cast(EmbeddingProvider, embedding_provider),
        embedding_model=embedding_model,
        embedding_api_key=embedding_api_key,
        embedding_base_url=embedding_base_url,
        embedding_dim=embedding_dim,
        embedding_batch=embedding_batch,
        environment=cast(Environment, environment),
        device=device,
        log_level=log_level,
        max_cache_size=max_cache_size,
        discord_enable=discord_enable,
        discord_token=discord_token,
        discord_public_key=discord_public_key,
        discord_app_id=discord_app_id,
        max_campaigns=max_campaigns,
        campaign_ttl=campaign_ttl,
        campaign_cleanup_interval=campaign_cleanup_interval,
        world=world,
    )
