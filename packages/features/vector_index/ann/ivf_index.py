import asyncio
import heapq
from typing import Any

from packages.features.vector_index.utils.similarity import cosine_similarity


class IVFIndex:
    def __init__(
        self,
        centroids: list[list[float]],
        inverted_lists: dict[int, list[str]],
        doc_to_cluster: dict[str, int],
        vector_store: Any,
        default_n_probe: int = 2,
    ) -> None:
        self.centroids = centroids
        self.inverted_lists = inverted_lists
        self.doc_to_cluster = doc_to_cluster
        self.vector_store = vector_store

        self.default_n_probe = default_n_probe

    # ---------------------------------------------------------
    # ANN CONTRACT
    # ---------------------------------------------------------

    async def search(self, query_vector: list[float], k: int = 10) -> list[str]:
        if not self.centroids:
            return []

        # -----------------------------------------------------
        # 🔥 1. definir n_probe (adaptativo)
        # -----------------------------------------------------
        n_probe = self._compute_n_probe(k)

        # -----------------------------------------------------
        # 🔥 2. selecionar clusters mais próximos
        # -----------------------------------------------------
        try:
            top_clusters = sorted(
                range(len(self.centroids)),
                key=lambda i: cosine_similarity(query_vector, self.centroids[i]),
                reverse=True,
            )[:n_probe]
        except Exception:
            return []

        # -----------------------------------------------------
        # 🔥 3. coletar candidatos
        # -----------------------------------------------------
        candidates: list[str] = []

        for cluster_id in top_clusters:
            candidates.extend(self.inverted_lists.get(cluster_id, []))

        if not candidates:
            return []

        # -----------------------------------------------------
        # 🔥 4. remover duplicados (importante!)
        # -----------------------------------------------------
        candidates = list(set(candidates))

        # -----------------------------------------------------
        # 🔥 5. rerank eficiente (heap)
        # -----------------------------------------------------
        # Busca vetores em paralelo para evitar gargalo de I/O
        tasks = [self.vector_store.get(doc_id) for doc_id in candidates]
        vectors = await asyncio.gather(*tasks)

        heap: list[tuple[float, str]] = []

        for doc_id, vec in zip(candidates, vectors, strict=False):
            if not vec:
                continue

            try:
                score = cosine_similarity(query_vector, vec)
            except Exception:
                continue

            item = (score, doc_id)

            if len(heap) < k:
                heapq.heappush(heap, item)
            else:
                heapq.heappushpop(heap, item)

        if not heap:
            return []

        # -----------------------------------------------------
        # 🔥 6. ordenar resultado final
        # -----------------------------------------------------
        heap.sort(reverse=True)

        return [doc_id for _, doc_id in heap]

    # ---------------------------------------------------------
    # INTERNALS
    # ---------------------------------------------------------

    def _compute_n_probe(self, k: int) -> int:
        """
        Define quantos clusters explorar (trade-off recall vs latência)
        """

        if len(self.centroids) <= 1:
            return 1

        if k <= 5:
            n_probe = 1
        elif k <= 10:
            n_probe = self.default_n_probe
        else:
            n_probe = self.default_n_probe + 1

        return min(n_probe, len(self.centroids))

    # ---------------------------------------------------------
    # OPTIONAL UTILS
    # ---------------------------------------------------------

    def get_cluster(self, doc_id: str) -> int | None:
        return self.doc_to_cluster.get(doc_id)
