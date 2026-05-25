from semantic_context_server.config.loader import load_settings
from semantic_context_server.config.profile import DEFAULT_PROFILE


def test_load_settings_uses_default_profile(monkeypatch):
    monkeypatch.delenv("APP_PROFILE", raising=False)
    monkeypatch.delenv("WORLD", raising=False)
    monkeypatch.setenv("APP_PROFILE", DEFAULT_PROFILE)
    monkeypatch.setenv("WORLD", "default")

    load_settings.cache_clear()
    settings = load_settings()

    assert settings.runtime.profile == DEFAULT_PROFILE
    assert settings.app.campaign_file == "./data"
    assert settings.app.world == "default"


def test_load_settings_uses_default_constants_when_env_missing(monkeypatch):
    monkeypatch.delenv("APP_PROFILE", raising=False)
    monkeypatch.delenv("STORAGE", raising=False)
    monkeypatch.delenv("WORLD", raising=False)

    load_settings.cache_clear()
    settings = load_settings()

    assert settings.runtime.profile == DEFAULT_PROFILE
    assert settings.app.campaign_file == "./data"
    assert settings.app.world == "default"
