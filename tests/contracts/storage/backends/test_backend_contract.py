from unittest.mock import AsyncMock, MagicMock

import pytest

from semantic_context_server.infrastructure.storage.backends.inmemory_backend import (
    InMemoryStorageBackend,
)
from semantic_context_server.infrastructure.storage.backends.json_backend import (
    JSONStorageBackend,
)


@pytest.fixture
def backends(tmp_path):
    executor = MagicMock()
    executor.run = AsyncMock(side_effect=lambda func, *args, **kwargs: func(*args, **kwargs))
    return [
        InMemoryStorageBackend(executor),
        JSONStorageBackend(tmp_path, executor),
    ]


@pytest.mark.contract
@pytest.mark.asyncio
async def test_backend_contract(backends):
    """❌ BASIC CONTRACT - Apenas operações básicas"""
    for backend in backends:
        ds = backend.build_document_store()

        await ds.set("k", {"v": 1})

        value = await ds.get("k")

        assert value == {"v": 1}


@pytest.mark.contract
@pytest.mark.parametrize(
    "backend_factory",
    [
        lambda tmp_path, executor: InMemoryStorageBackend(executor),
        lambda tmp_path, executor: JSONStorageBackend(tmp_path, executor),
    ],
)
def test_backend_returns_adapters(backend_factory, tmp_path):
    """✅ ADAPTER_INTERFACE - Valida que backends retornam adapters com interface correta"""
    executor = MagicMock()
    backend = backend_factory(tmp_path, executor)

    assert hasattr(backend.build_document_store(), "set")
    assert hasattr(backend.build_vector_store(), "search")
    assert hasattr(backend.build_metadata_store(), "get")
    assert hasattr(backend.build_token_store(), "set")


@pytest.mark.contract
@pytest.mark.asyncio
async def test_backend_document_operations(tmp_path):
    """✅ DOCUMENT_OPS - Valida operações completas de documento"""
    executor = MagicMock()
    executor.run = AsyncMock(side_effect=lambda func, *args, **kwargs: func(*args, **kwargs))

    for backend in [InMemoryStorageBackend(executor), JSONStorageBackend(tmp_path, executor)]:
        ds = backend.build_document_store()

        # Set
        doc = {"title": "Test", "content": "Data"}
        await ds.set("test_doc", doc)

        # Get
        result = await ds.get("test_doc")
        assert result == doc

        # Update
        updated = {"title": "Test Updated", "content": "New Data"}
        await ds.set("test_doc", updated)
        result = await ds.get("test_doc")
        assert result == updated


@pytest.mark.contract
@pytest.mark.asyncio
async def test_backend_metadata_operations(tmp_path):
    """✅ METADATA_OPS - Valida operações de metadata"""
    executor = MagicMock()
    executor.run = AsyncMock(side_effect=lambda func, *args, **kwargs: func(*args, **kwargs))

    for backend in [InMemoryStorageBackend(executor), JSONStorageBackend(tmp_path, executor)]:
        ms = backend.build_metadata_store()

        # Set metadata
        meta = {"author": "System", "created": "2026-04-14"}
        await ms.set("meta_key", meta)

        # Get metadata
        result = await ms.get("meta_key")
        assert result == meta


@pytest.mark.contract
@pytest.mark.asyncio
async def test_backend_token_operations(tmp_path):
    """✅ TOKEN_OPS - Valida operações de tokens"""
    executor = MagicMock()
    executor.run = AsyncMock(side_effect=lambda func, *args, **kwargs: func(*args, **kwargs))

    for backend in [InMemoryStorageBackend(executor), JSONStorageBackend(tmp_path, executor)]:
        ts = backend.build_token_store()

        # Set tokens
        token_data = {"count": 1024, "model": "gpt-4"}
        await ts.set("token_key", token_data)

        # Get tokens
        result = await ts.get("token_key")
        assert result == token_data


@pytest.mark.contract
@pytest.mark.asyncio
async def test_backend_clear_all(tmp_path):
    """✅ CLEAR_ALL - Valida limpeza completa"""
    executor = MagicMock()
    executor.run = AsyncMock(side_effect=lambda func, *args, **kwargs: func(*args, **kwargs))

    for backend in [InMemoryStorageBackend(executor), JSONStorageBackend(tmp_path, executor)]:
        ds = backend.build_document_store()

        # Add multiple documents
        await ds.set("d1", {"data": "a"})
        await ds.set("d2", {"data": "b"})

        # Clear
        await ds.clear()

        # Verify cleared
        assert await ds.get("d1") is None
        assert await ds.get("d2") is None


@pytest.mark.contract
@pytest.mark.asyncio
async def test_backend_isolation(tmp_path):
    """✅ ISOLATION - Valida isolamento entre stores"""
    executor = MagicMock()
    executor.run = AsyncMock(side_effect=lambda func, *args, **kwargs: func(*args, **kwargs))

    backend = JSONStorageBackend(tmp_path, executor)

    ds = backend.build_document_store()
    ms = backend.build_metadata_store()
    ts = backend.build_token_store()

    # Set in different stores
    await ds.set("key", {"doc": "data"})
    await ms.set("key", {"meta": "data"})
    await ts.set("key", {"token": "data"})

    # Verify isolation (same key, different values)
    assert await ds.get("key") == {"doc": "data"}
    assert await ms.get("key") == {"meta": "data"}
    assert await ts.get("key") == {"token": "data"}
