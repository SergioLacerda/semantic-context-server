import json
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

from semantic_context_server.infrastructure.storage.kv.json_kv_store import (
    JSONKeyValueStore,
)
from tests.config.helpers.io import read_text_utf8


@pytest.fixture
def executor():
    """
    Fixture que emula o comportamento do ExecutorPort.
    O objeto é síncrono, mas o método .run() é assíncrono.
    """
    mock = MagicMock(spec=["run"])

    async def mock_run(fn, *args, **kwargs):
        return fn(*args, **kwargs)

    mock.run = AsyncMock(side_effect=mock_run)
    return mock


@pytest.mark.asyncio
async def test_set_and_get(tmp_path: Path, executor):
    path = tmp_path / "store.json"

    store = JSONKeyValueStore(path, executor)

    await store.set("a", 1)

    result = await store.get("a")

    assert result == 1


@pytest.mark.asyncio
async def test_get_missing_key(tmp_path: Path, executor):
    path = tmp_path / "store.json"

    store = JSONKeyValueStore(path, executor)

    result = await store.get("missing")

    assert result is None


@pytest.mark.asyncio
async def test_persists_to_file(tmp_path: Path, executor):
    path = tmp_path / "store.json"

    store = JSONKeyValueStore(path, executor)

    await store.set("a", 1)

    data = json.loads(read_text_utf8(path))

    assert data == {"a": 1}


@pytest.mark.asyncio
async def test_multiple_sets(tmp_path: Path, executor):
    path = tmp_path / "store.json"

    store = JSONKeyValueStore(path, executor)

    await store.set("a", 1)
    await store.set("b", 2)

    val_a = await store.get("a")
    val_b = await store.get("b")

    assert val_a == 1
    assert val_b == 2


@pytest.mark.asyncio
async def test_overwrite_value(tmp_path: Path, executor):
    path = tmp_path / "store.json"

    store = JSONKeyValueStore(path, executor)

    await store.set("a", 1)
    await store.set("a", 2)

    result = await store.get("a")

    assert result == 2


@pytest.mark.asyncio
async def test_clear(tmp_path: Path, executor):
    path = tmp_path / "store.json"

    store = JSONKeyValueStore(path, executor)

    await store.set("a", 1)
    await store.clear()

    result = await store.get("a")
    assert result is None

    data = json.loads(read_text_utf8(path))
    assert data == {}


@pytest.mark.asyncio
async def test_get_with_nonexistent_file(tmp_path: Path, executor):
    path = tmp_path / "store.json"

    store = JSONKeyValueStore(path, executor)

    result = await store.get("a")

    assert result is None
