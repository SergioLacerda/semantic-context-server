import pytest

from packages.core.runtime_config.profile import (
    DEFAULT_PROFILE,
    build_profile,
    get_profile_defaults,
)


def test_get_profile_defaults_local():
    defaults = get_profile_defaults(DEFAULT_PROFILE)

    assert defaults["storage"] == "json"
    assert defaults["llm_provider"] == "lmstudio"
    assert defaults["embedding_provider"] == "sentence"


def test_get_profile_defaults_invalid_profile_raises():
    with pytest.raises(ValueError, match="Invalid APP_PROFILE"):
        get_profile_defaults("invalid-profile")


def test_build_profile_accepts_valid_settings():
    profile = build_profile(
        profile=DEFAULT_PROFILE,
        storage="json",
        campaign_file="data",
        rotation_size=1,
        max_entries_per_file=10,
        llm_provider="openai",
        llm_model="gpt-4o-mini",
        llm_api_key=None,
        llm_base_url=None,
        llm_timeout=10,
        embedding_provider="openai",
        embedding_model="text-embedding-3-small",
        embedding_api_key=None,
        embedding_base_url=None,
        embedding_dim=1536,
        embedding_batch=32,
        environment="dev",
        device=None,
        log_level=20,
        max_cache_size=100,
        discord_enable=None,
        discord_token=None,
        discord_public_key=None,
        discord_app_id=None,
        max_campaigns=5,
        campaign_ttl=600,
        campaign_cleanup_interval=30,
        world="default",
    )

    assert profile.profile == DEFAULT_PROFILE
    assert profile.llm_provider == "openai"
    assert profile.embedding_provider == "openai"
    assert profile.max_campaigns == 5
