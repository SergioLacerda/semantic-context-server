import logging
from typing import Any

import numpy as np

logger = logging.getLogger("semantic_context_server.ann.faiss")


class FaissANN:
    def __init__(self, index: Any, id_map: list[str]) -> None:
        """
        index: faiss.Index
        id_map: lista que mapeia índice → doc_id
        """
        self.index = index
        self.id_map = id_map

    def search(self, query_vector: list[float], k: int = 10) -> list[str]:
        if not self.index:
            return []

        try:
            vec = np.array([query_vector]).astype("float32")

            distances, indices = self.index.search(vec, k)

            results = []
            for idx in indices[0]:
                if idx < 0 or idx >= len(self.id_map):
                    continue
                results.append(self.id_map[idx])

            return results

        except Exception:
            logger.exception("Faiss search failed")
            return []
