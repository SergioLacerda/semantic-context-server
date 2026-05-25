import pytest

from semantic_context_server.infrastructure.storage.backends.base_backend import StorageBackend
from tests.config.fakes.infrastructure.storage.fake_storage_config import FakeStorageConfig


class IncompleteBackend(StorageBackend):
    pass


class DummyBackend(StorageBackend):
    def build_vector_store(self):
        return "vector"

    def build_document_store(self):
        return "doc"

    def build_token_store(self):
        return "token"

    def build_metadata_store(self):
        return "meta"


def test_storage_backend_contract():
    backend = DummyBackend()

    assert backend.build_vector_store() == "vector"
    assert backend.build_document_store() == "doc"
    assert backend.build_token_store() == "token"
    assert backend.build_metadata_store() == "meta"


def test_storage_backend_is_abstract():
    with pytest.raises(TypeError):
        StorageBackend()  # type: ignore[abstract]


def test_storage(container_factory):
    config = FakeStorageConfig(namespace="inmemory")

    container = container_factory(storage_config=config)

    assert container is not None


def test_incomplete_backend_fails():
    with pytest.raises(TypeError):
        IncompleteBackend()  # type: ignore[abstract]
