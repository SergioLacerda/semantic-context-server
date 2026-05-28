import os

import pytest

from packages.core.runtime_config.env import (
    DEFAULT_ENVIRONMENT,
    ENV_FILE_BASE,
    ENV_FILE_LOCAL,
    get_env_files,
    load_environment,
    parse_cli_overrides,
)
from tests.config.helpers.io import write_text_utf8


def test_get_env_files_returns_ordered_list():
    env = "test"
    files = get_env_files(env)

    expected = [
        f"{ENV_FILE_BASE}.{env}.local",
        ENV_FILE_LOCAL,
        f"{ENV_FILE_BASE}.{env}",
        ENV_FILE_BASE,
    ]

    assert len(files) == 4
    for i, expected_name in enumerate(expected):
        assert files[i].name == expected_name


def test_parse_cli_overrides_extracts_key_value_pairs():
    # Simulate CLI args
    original_argv = ["script.py", "--KEY1=value1", "--key2=value2", "not-an-arg"]

    with pytest.MonkeyPatch().context() as m:
        m.setattr("sys.argv", original_argv)

        overrides = parse_cli_overrides()

        assert overrides == {"KEY1": "value1", "KEY2": "value2"}


def test_parse_cli_overrides_ignores_invalid_args():
    original_argv = ["script.py", "not-an-arg", "--invalid", "--=value", "--key="]

    with pytest.MonkeyPatch().context() as m:
        m.setattr("sys.argv", original_argv)

        overrides = parse_cli_overrides()

        assert overrides == {}


def test_load_environment_uses_default_when_no_env_set(monkeypatch):
    monkeypatch.delenv("ENVIRONMENT", raising=False)

    env, loaded_files, cli_overrides = load_environment()

    assert env == DEFAULT_ENVIRONMENT
    assert isinstance(loaded_files, list)
    assert isinstance(cli_overrides, dict)


def test_load_environment_loads_existing_files(tmp_path, monkeypatch):
    # Create temporary .env files
    env_file = tmp_path / ".env"
    write_text_utf8(env_file, "TEST_VAR=global")

    env_test_file = tmp_path / ".env.test"
    write_text_utf8(env_test_file, "TEST_VAR=test")

    # Mock ROOT to use tmp_path
    monkeypatch.setattr("packages.core.runtime_config.env.ROOT", tmp_path)
    monkeypatch.setenv("ENVIRONMENT", "test")

    env, loaded_files, cli_overrides = load_environment()

    assert env == "test"
    assert ".env.test" in loaded_files
    assert ".env" in loaded_files
    assert os.getenv("TEST_VAR") == "test"  # .env.test should override .env
