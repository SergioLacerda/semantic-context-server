import asyncio
import logging
from typing import Any

from packages.core.shared_kernel.execution import ExecutorPort
from packages.features.vector_index.components import VectorReader

logger = logging.getLogger(__name__)


class IVFBuilder:
    """
    Implementação do construtor de índice ANN seguindo a regra de Sync Adapters.
    ✔ Coleta de vetores assíncrona
    ✔ Treinamento de índice CPU-bound via Executor
    """

    def __init__(self, executor: ExecutorPort):
        self.executor = executor

    async def build(self, doc_ids: list[str], vector_reader: VectorReader) -> Any:
        # 1. Busca os vetores de forma concorrente (Async I/O)
        # Usamos gather para não serializar as esperas do storage
        tasks = [vector_reader.get(d_id) for d_id in doc_ids]
        results = await asyncio.gather(*tasks)

        vectors = [v for v in results if v is not None]

        if not vectors:
            logger.warning("No vectors found to build ANN index")
            return None

        # 2. Despacha a lógica de treinamento para o pool de threads
        # Isso evita bloquear o Event Loop durante cálculos matemáticos pesados.
        logger.debug("Starting heavy index training for %d vectors", len(vectors))
        index = await self.executor.run(self._build_index_sync, vectors, doc_ids)

        return index

    def _build_index_sync(self, vectors: list[list[float]], doc_ids: list[str]) -> Any:
        """Lógica puramente síncrona de treinamento (K-Means, Clusterização, etc)."""
        # Exemplo: Aqui você integraria com faiss, scikit-learn ou sua implementação própria
        # return faiss_index.train(vectors)
        return {"vectors_count": len(vectors), "status": "trained"}
