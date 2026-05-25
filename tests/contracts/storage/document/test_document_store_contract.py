from unittest.mock import AsyncMock, MagicMock

import pytest

from semantic_context_server.infrastructure.storage.adapters.document_store import (
    DocumentStoreAdapter,
)
from tests.config.fakes.infrastructure.storage.fake_kv_store import FakeKVStore

# =========================================================
# TESTS
# =========================================================


@pytest.mark.contract
@pytest.mark.asyncio
async def test_document_store_contract():
    """❌ BASIC CONTRACT - Apenas operações básicas (LEGADO)"""
    kv = FakeKVStore()
    store = kv

    assert await store.get("missing") is None

    await store.set("k", {"v": 1})
    assert await store.get("k") == {"v": 1}

    await store.set("k", {"v": 2})
    assert await store.get("k") == {"v": 2}

    await store.clear()
    assert await store.get("k") is None


@pytest.mark.contract
@pytest.mark.asyncio
async def test_document_store_adapter():
    """✅ ADAPTER CONTRACT - Valida DocumentStoreAdapter com async KV"""
    kv = FakeKVStore()
    executor = MagicMock()
    executor.run = AsyncMock(side_effect=lambda func, *args, **kwargs: func(*args, **kwargs))

    store = DocumentStoreAdapter(kv, executor)

    # Set/Get valid document
    doc = {"title": "Example", "content": "Data"}
    await store.set("doc1", doc)
    result = await store.get("doc1")
    assert result == doc


@pytest.mark.contract
@pytest.mark.asyncio
async def test_document_store_validation():
    """✅ VALIDATION - Valida validações do DocumentStoreAdapter"""
    kv = FakeKVStore()
    executor = MagicMock()
    executor.run = AsyncMock(side_effect=lambda func, *args, **kwargs: func(*args, **kwargs))

    store = DocumentStoreAdapter(kv, executor)

    # Empty key validation
    with pytest.raises(ValueError):
        await store.set("", {"content": "data"})

    # Non-dict validation
    with pytest.raises(TypeError):
        await store.set("doc1", "not a dict")

    # Get empty key returns None
    result = await store.get("")
    assert result is None


@pytest.mark.contract
@pytest.mark.asyncio
async def test_document_store_clear():
    """✅ CLEAR - Valida limpeza de documento"""
    kv = FakeKVStore()
    executor = MagicMock()
    executor.run = AsyncMock(side_effect=lambda func, *args, **kwargs: func(*args, **kwargs))

    store = DocumentStoreAdapter(kv, executor)

    # Add documents
    await store.set("d1", {"data": "a"})
    await store.set("d2", {"data": "b"})

    # Clear
    await store.clear()

    # Verify all cleared
    assert await store.get("d1") is None
    assert await store.get("d2") is None


@pytest.mark.contract
@pytest.mark.asyncio
async def test_document_store_multiple_documents():
    """✅ MULTIPLE_DOCS - Valida múltiplos documentos"""
    kv = FakeKVStore()
    executor = MagicMock()
    executor.run = AsyncMock(side_effect=lambda func, *args, **kwargs: func(*args, **kwargs))

    store = DocumentStoreAdapter(kv, executor)

    docs = {
        "user:1": {"name": "Alice", "age": 30},
        "user:2": {"name": "Bob", "age": 25},
        "post:1": {"title": "Hello", "body": "World"},
    }

    for doc_id, doc in docs.items():
        await store.set(doc_id, doc)

    for doc_id, doc in docs.items():
        assert await store.get(doc_id) == doc


@pytest.mark.contract
@pytest.mark.asyncio
async def test_document_store_overwrite():
    """✅ OVERWRITE - Valida sobrescrita de documentos"""
    kv = FakeKVStore()
    executor = MagicMock()
    executor.run = AsyncMock(side_effect=lambda func, *args, **kwargs: func(*args, **kwargs))

    store = DocumentStoreAdapter(kv, executor)

    doc_id = "versioned"

    # V1
    await store.set(doc_id, {"version": 1})
    assert await store.get(doc_id) == {"version": 1}

    # V2
    await store.set(doc_id, {"version": 2})
    assert await store.get(doc_id) == {"version": 2}

    # V3
    await store.set(doc_id, {"version": 3, "nested": {"data": "here"}})
    assert await store.get(doc_id) == {"version": 3, "nested": {"data": "here"}}


@pytest.mark.contract
@pytest.mark.asyncio
async def test_document_store_complex_schema():
    """✅ COMPLEX_SCHEMA - Valida documentos complexos"""
    kv = FakeKVStore()
    executor = MagicMock()
    executor.run = AsyncMock(side_effect=lambda func, *args, **kwargs: func(*args, **kwargs))

    store = DocumentStoreAdapter(kv, executor)

    complex_doc = {
        "id": "doc1",
        "title": "Complex Document",
        "metadata": {
            "author": "System",
            "created": "2026-04-14",
            "tags": ["test", "contract"],
            "version": 1,
        },
        "content": {
            "sections": [
                {"name": "Intro", "text": "Introduction text"},
                {"name": "Body", "text": "Body text"},
            ],
            "references": ["ref1", "ref2"],
        },
        "flags": [True, False, True],
    }

    await store.set("complex", complex_doc)
    result = await store.get("complex")
    assert result == complex_doc


@pytest.mark.contract
@pytest.mark.asyncio
async def test_document_store_sync_kv_compatibility():
    """✅ SYNC_KV_COMPAT - Valida DocumentStoreAdapter com sync KV store"""

    class SyncKVStore:
        def __init__(self):
            self._data = {}

        def get(self, key):
            return self._data.get(key)

        def set(self, key, value):
            self._data[key] = value

        def clear(self):
            self._data.clear()

    sync_kv = SyncKVStore()
    executor = MagicMock()
    executor.run = AsyncMock(side_effect=lambda func, *args, **kwargs: func(*args, **kwargs))

    store = DocumentStoreAdapter(sync_kv, executor)

    # Must work with sync store
    await store.set("sync_doc", {"data": "from_sync_store"})
    result = await store.get("sync_doc")
    assert result == {"data": "from_sync_store"}
