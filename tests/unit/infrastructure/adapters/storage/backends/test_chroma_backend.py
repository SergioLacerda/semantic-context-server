from unittest.mock import MagicMock

import pytest

from semantic_context_server.infrastructure.storage.backends.chroma_backend import (
    ChromaStorageBackend,
)


def test_chroma_backend_builds():
    pytest.importorskip("chromadb")

    # Usar MagicMock com spec para garantir conformidade com o Port
    executor = MagicMock(spec=["run"])
    backend = ChromaStorageBackend(executor)

    assert backend.build_vector_store() is not None
