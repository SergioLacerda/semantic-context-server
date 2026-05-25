from collections.abc import Sequence
from typing import Any

from semantic_context_server.vector_index.utils.similarity import cosine_similarity


class LazyVectorSimilarity:
    """
    Calcula similaridade vetorial sob demanda (lazy).

    - evita recomputar embeddings
    - cacheia resultados por doc_id
    - usa cosine similarity
    """

    def __init__(self, vector_store: Any) -> None:
        self.vector_store = vector_store
        self._cache: dict[str, float] = {}

    # ---------------------------------------------------------
    # public API
    # ---------------------------------------------------------

    def similarity(self, query_vector: Sequence[float] | Any, doc_id: str) -> float:
        if doc_id in self._cache:
            return self._cache[doc_id]

        doc_vector = self.vector_store.get(doc_id)

        if not doc_vector:
            score = 0.0
        else:
            score = cosine_similarity(query_vector, doc_vector)

        self._cache[doc_id] = score

        return score
