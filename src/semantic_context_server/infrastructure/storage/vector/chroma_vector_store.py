from typing import Any


class ChromaVectorStore:
    """Synchronous wrapper around a Chroma collection.

    Wrapped by ``VectorStoreAdapter`` to expose the async ``VectorStorePort`` API.
    """

    def __init__(self, collection: Any) -> None:
        self.collection = collection

    def add(self, doc_id: str, vector: list[float]) -> None:
        self.collection.add(
            ids=[doc_id],
            embeddings=[vector],
        )

    def get(self, doc_id: str) -> list[float] | None:
        result = self.collection.get(ids=[doc_id])

        if not result or not result.get("embeddings"):
            return None

        first: list[float] = result["embeddings"][0]
        return first

    def keys(self) -> list[str]:
        result = self.collection.get()

        if not result or not result.get("ids"):
            return []

        ids: list[str] = result["ids"]
        return ids

    def search(self, query_vector: list[float], k: int) -> list[str]:
        results = self.collection.query(
            query_embeddings=[query_vector],
            n_results=k,
        )

        if results.get("ids"):
            first_match: list[str] = results["ids"][0]
            return first_match
        return []

    def clear(self) -> None:
        self.collection.delete(where={})
