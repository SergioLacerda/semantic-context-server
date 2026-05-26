from typing import Any


class SimpleClusterRouter:
    """
    Implementação padrão de ClusterRouter.

    ✔ 1 item por cluster
    ✔ trabalha com doc_ids
    ✔ não depende de embeddings
    """

    def __init__(self, cluster_manager: Any) -> None:
        self.manager = cluster_manager

    async def route(self, candidates: list[str]) -> list[str]:
        seen: set[tuple[str, ...]] = set()
        result: list[str] = []

        for doc_id in candidates:
            cluster = self.manager.get_cluster(doc_id)

            if not cluster:
                result.append(doc_id)
                continue

            cluster_id = tuple(sorted(cluster))

            if cluster_id in seen:
                continue

            seen.add(cluster_id)
            result.append(doc_id)

        return result
