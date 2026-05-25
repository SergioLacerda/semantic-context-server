from unittest.mock import AsyncMock, MagicMock

import pytest

from semantic_context_server.infrastructure.storage.backends.json_backend import (
    JSONStorageBackend,
)


@pytest.mark.asyncio
async def test_json_backend_builds(tmp_path):
    executor = MagicMock()
    executor.run = AsyncMock(side_effect=lambda func, *args, **kwargs: func(*args, **kwargs))
    backend = JSONStorageBackend(tmp_path, executor)

    vector = backend.build_vector_store()
    doc = backend.build_document_store()

    # Store adapters wrap backend calls in async
    await vector.add("a", [1, 0])
    result = await vector.get("a")
    assert result == [1, 0]

    # Document store also async via adapter
    await doc.set("a", {"x": 1})
    doc_result = await doc.get("a")

    assert doc_result is not None
    assert doc_result["x"] == 1


def test_json_backend_build_token_store(tmp_path):
    executor = MagicMock()
    backend = JSONStorageBackend(tmp_path, executor)

    store = backend.build_token_store()

    assert store is not None


def test_json_backend_build_metadata_store(tmp_path):
    executor = MagicMock()
    backend = JSONStorageBackend(tmp_path, executor)

    store = backend.build_metadata_store()

    assert store is not None
