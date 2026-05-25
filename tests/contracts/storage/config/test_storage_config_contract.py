from pathlib import Path

from tests.config.fakes.infrastructure.storage.fake_storage_config import FakeStorageConfig


def test_storage_config_returns_path():
    config = FakeStorageConfig()

    path = config.get_base_path("c1")

    assert isinstance(path, Path)
