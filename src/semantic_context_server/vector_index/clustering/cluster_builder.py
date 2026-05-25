from typing import Any

from semantic_context_server.vector_index.utils.similarity import batch_cosine_similarity


class ClusterBuilder:
    def __init__(self, threshold: float = 0.75) -> None:
        self.threshold = threshold

    def build(self, doc_ids: list[str], vector_store: Any) -> list[list[str]]:
        clusters: list[list[str]] = []
        visited: set[str] = set()

        # pré-carregar vetores
        vectors = {doc_id: vector_store.get(doc_id) for doc_id in doc_ids}

        for i, base_id in enumerate(doc_ids):
            if base_id in visited:
                continue

            base_vec = vectors[base_id]

            # pegar vetores restantes
            remaining_ids = doc_ids[i + 1 :]
            remaining_vecs = [vectors[rid] for rid in remaining_ids]

            sims = batch_cosine_similarity(base_vec, remaining_vecs)

            cluster = [base_id]
            visited.add(base_id)

            for rid, sim in zip(remaining_ids, sims, strict=False):
                if sim >= self.threshold:
                    cluster.append(rid)
                    visited.add(rid)

            clusters.append(cluster)

        return clusters
