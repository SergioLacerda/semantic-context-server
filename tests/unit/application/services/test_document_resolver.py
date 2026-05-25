from typing import Any

from semantic_context_server.application.services.document_resolver import (
    DocumentResolver,
)


def test_resolve_basic():
    docs = {"1": {"text": "hello"}}
    meta = {"1": {"score": 0.9}}

    resolver = DocumentResolver(docs, meta)

    result = resolver.resolve(["1"])

    assert result == [
        {
            "id": "1",
            "text": "hello",
            "score": 0.9,
            "metadata": {"score": 0.9},
        }
    ]


def test_resolve_missing_document():
    docs: dict[str, dict] = {}
    meta: dict[str, dict] = {"1": {"score": 0.5}}

    resolver = DocumentResolver(docs, meta)

    result = resolver.resolve(["1"])

    assert result[0]["text"] == ""


def test_resolve_missing_metadata():
    docs: dict[str, dict] = {"1": {"text": "hello"}}
    meta: dict[str, dict] = {}

    resolver = DocumentResolver(docs, meta)

    result = resolver.resolve(["1"])

    assert result[0]["score"] == 0
    assert result[0]["metadata"] == {}


def test_resolve_missing_fields():
    docs: dict[str, dict[str, Any]] = {}
    meta: dict[str, dict[str, Any]] = {}

    resolver = DocumentResolver(docs, meta)

    result = resolver.resolve(["1"])

    assert result[0]["text"] == ""
    assert result[0]["score"] == 0


def test_resolve_multiple():
    docs: dict[str, dict] = {
        "1": {"text": "a"},
        "2": {"text": "b"},
    }
    meta: dict[str, dict] = {
        "1": {"score": 0.1},
        "2": {"score": 0.2},
    }

    resolver = DocumentResolver(docs, meta)

    result = resolver.resolve(["1", "2"])

    assert len(result) == 2
    assert result[1]["text"] == "b"
