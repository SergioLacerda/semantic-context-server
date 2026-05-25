import logging
from typing import Any

logger = logging.getLogger("semantic_context_server.ann.qdrant")


class QdrantANN:
    def __init__(self, client: Any, collection_name: str) -> None:
        self.client = client
        self.collection = collection_name

    def search(self, query_vector: list[float], k: int = 10) -> list[str]:
        try:
            hits = self.client.search(
                collection_name=self.collection,
                query_vector=query_vector,
                limit=k,
            )

            return [str(hit.id) for hit in hits]

        except Exception:
            logger.exception("Qdrant search failed")
            return []
