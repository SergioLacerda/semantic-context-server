import asyncio
import logging
from typing import Any

from semantic_context_server.application.ports.executor import ExecutorPort
from packages.features.vector_index.components import VectorReader

logger = logging.getLogger(__name__)


class ClusterManager:
    """
    Gerenciador de clusters seguindo a regra de Sync Adapters.
    ✔ Coleta de vetores assíncrona via gather
    ✔ Processamento de clustering CPU-bound via Executor
    """

    def __init__(self, cluster_builder: Any, executor: ExecutorPort) -> None:
        self.cluster_builder = cluster_builder
        self.executor = executor
        self._clusters: dict[Any, list[str]] = {}

    async def update(self, doc_ids: list[str], vector_reader: VectorReader) -> None:
        # 1. Busca os vetores de forma concorrente (Async I/O)
        tasks = [vector_reader.get(d_id) for d_id in doc_ids]
        results = await asyncio.gather(*tasks)

        # Cria um mapeamento de ID -> Vetor para o processamento
        vector_data = {d_id: v for d_id, v in zip(doc_ids, results, strict=False) if v is not None}

        if not vector_data:
            logger.warning("No vectors found for cluster update")
            return

        # 2. Delega a lógica de agrupamento para o Executor (CPU-bound)
        logger.debug("Starting cluster computation for %d vectors", len(vector_data))

        # O executor garante que o loop de eventos continue livre
        self._clusters = await self.executor.run(self._compute_clusters_sync, vector_data)

        logger.info("Clustering update complete")

    def get_cluster(self, doc_id: str) -> list[str] | None:
        return self._clusters.get(doc_id)

    def _compute_clusters_sync(self, data: dict[str, list[float]]) -> Any:
        """Lógica síncrona de clustering delegada ao cluster_builder."""
        return self.cluster_builder.build(data)
