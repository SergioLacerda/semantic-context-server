from pathlib import Path

import pytest

from semantic_context_server.infrastructure.storage.vector.json_vector_store import (
    JSONVectorStore,
)
from semantic_context_server.infrastructure.storage.vector_store_config import (
    VectorStoreConfig,
)
from tests.config.helpers.io import write_text_utf8


@pytest.fixture
def store(tmp_path):
    return JSONVectorStore(tmp_path / "vec.json")


def test_add_and_get(store):
    store.add("doc1", [1.0, 0.0])

    assert store.get("doc1") == [1.0, 0.0]


def test_keys(store):
    store.add("a", [1, 0])
    store.add("b", [0, 1])

    assert set(store.keys()) == {"a", "b"}


def test_clear(store):
    store.add("a", [1, 0])

    store.clear()

    assert store.keys() == []


def test_search_basic(store):
    store.add("a", [1, 0])
    store.add("b", [0, 1])

    assert store.search([1, 0], k=1) == ["a"]


def test_search_empty(store):
    assert store.search([1, 0], k=1) == []


def test_persistence(tmp_path):
    path = tmp_path / "vec.json"

    store = JSONVectorStore(path)
    store.add("doc1", [1, 0])

    new_store = JSONVectorStore(path)

    assert new_store.get("doc1") == [1, 0]


def test_get_file_size_kb_file_not_exists():
    path = Path("non_existent.json")

    size = JSONVectorStore._get_file_size_kb(path)

    assert size == 0.0


def test_rotation_trigger_by_size(tmp_path):
    path = tmp_path / "store.json"

    config = VectorStoreConfig(
        enable_rotation=True,
        rotation_size=1,
        max_entries_per_file=1000,
    )

    store = JSONVectorStore(path, config)

    store.add("doc1", [1.0, 2.0, 3.0])

    assert path.exists()


def test_no_rotation_when_disabled(tmp_path):
    path = tmp_path / "store.json"

    config = VectorStoreConfig(enable_rotation=False)

    store = JSONVectorStore(path, config)

    store.add("doc1", [1, 2, 3])

    assert path.exists()


def test_should_rotate_by_entries(tmp_path):
    path = tmp_path / "store.json"

    config = VectorStoreConfig(
        enable_rotation=True,
        max_entries_per_file=1,
    )

    store = JSONVectorStore(path, config)

    store.add("doc1", [1])
    store.add("doc2", [2])

    assert path.exists()


def test_rotate_file_no_file(tmp_path):
    path = tmp_path / "store.json"

    store = JSONVectorStore(path)

    store._rotate_file()


def test_rotate_file_renames(tmp_path):
    path = tmp_path / "store.json"

    store = JSONVectorStore(path)

    write_text_utf8(path, "{}")

    store._rotate_file()

    assert not path.exists()

    files = list(tmp_path.glob("store_*.json"))

    assert len(files) == 1


def test_persist_with_empty_cache_does_nothing(tmp_path):
    path = tmp_path / "vectors.json"

    store = JSONVectorStore(path)

    assert store._cache is None

    store._persist()

    assert not path.exists()
