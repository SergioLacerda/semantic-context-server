import asyncio
import logging
from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import Any, Protocol, runtime_checkable

from semantic_context_server.application.ports.executor import ExecutorPort
from semantic_context_server.application.ports.storage import (
    DocumentStorePort,
    MetadataStorePort,
    TokenStorePort,
)

logger = logging.getLogger("semantic_context_server.vector_index.components")

# ==========================================================
# CQRS - SEPARAÇÃO DE LEITURA E ESCRITA
# ==========================================================


@runtime_checkable
class ManagedComponent(Protocol):
    async def start(self) -> None: ...
    async def stop(self) -> None: ...


@runtime_checkable
class VectorReader(Protocol):
    async def search(self, vector: list[float], limit: int) -> list[str]: ...
    async def get(self, doc_id: str) -> Any: ...


@runtime_checkable
class VectorWriter(Protocol):
    async def add(self, doc_id: str, vector: list[float], metadata: dict) -> None: ...
    async def clear(self) -> None: ...


# ==========================================================
# PROTOCOLS (CONTRATOS NÃO-STORAGE)
# ==========================================================


@runtime_checkable
class Ranker(Protocol):
    async def rank(self, ctx: Any, candidates: list[str]) -> list[str]: ...


@runtime_checkable
class QueryClassifier(Protocol):
    async def classify(self, query: str) -> str: ...


@runtime_checkable
class IVFBuilder(Protocol):
    async def build(self, doc_ids: list[str], vector_reader: VectorReader) -> Any: ...


@runtime_checkable
class IVFRouter(Protocol):
    def set_index(self, index: Any) -> None: ...
    async def route(self, query_vector: list[float]) -> Iterable[str]: ...
    async def search(self, query_vector: list[float], k: int = 10) -> list[str]: ...


@runtime_checkable
class ClusterManager(Protocol):
    async def update(self, doc_ids: list[str], vector_reader: VectorReader) -> None: ...
    def get_cluster(self, doc_id: str) -> list[str] | None: ...


@runtime_checkable
class ClusterRouter(Protocol):
    async def route(self, candidates: list[str]) -> list[str]: ...


# ==========================================================
# COMPONENT CONTAINER
# ==========================================================


@dataclass(slots=True)
class VectorIndexComponents:
    """
    Boundary do sub-sistema de busca vetorial.

    ✔ Contratos centralizados na camada application
    ✔ Duck typing consistente
    ✔ Sem duplicação de interfaces
    ✔ Independente de infra
    """

    # ---------------------------------------------------------
    # classificação / controle
    # ---------------------------------------------------------

    query_classifier: QueryClassifier

    # ---------------------------------------------------------
    # ranking
    # ---------------------------------------------------------

    stage1_ranker: Ranker
    stage2_ranker: Ranker
    final_ranker: Ranker

    # ---------------------------------------------------------
    # stores (PORTS OFICIAIS)
    # ---------------------------------------------------------

    executor: ExecutorPort
    vector_reader: VectorReader
    vector_writer: VectorWriter
    document_store: DocumentStorePort
    token_store: TokenStorePort
    metadata_store: MetadataStorePort

    # ---------------------------------------------------------
    # ANN
    # ---------------------------------------------------------

    ivf_builder: IVFBuilder
    ivf_router: IVFRouter

    # ---------------------------------------------------------
    # clustering
    # ---------------------------------------------------------

    cluster_manager: ClusterManager

    # ---------------------------------------------------------
    # runtime / infra
    # ---------------------------------------------------------

    deduplicator: Any | None = None
    # Rastreia tarefas de background (como inicialização de ANN)
    _background_tasks: list[asyncio.Task] = field(default_factory=list)

    cluster_router: ClusterRouter | None = None

    # ---------------------------------------------------------
    # narrativa (opcional)
    # ---------------------------------------------------------

    temporal_index: Any | None = None
    causal_graph: Any | None = None

    # ---------------------------------------------------------
    # config
    # ---------------------------------------------------------

    vector_dim: int = 768

    # ==========================================================
    # CONSTANTES DE CONTRATO (ANTI-ERRO HUMANO)
    # ==========================================================

    KV_METHODS = ["get", "set"]
    READER_METHODS = ["get", "search"]
    WRITER_METHODS = ["add", "clear"]

    # ==========================================================
    # VALIDATION HELPERS
    # ==========================================================

    def _validate_store(self, store: Any, methods: list[str], name: str) -> None:
        missing = [m for m in methods if not hasattr(store, m)]
        if missing:
            raise TypeError(
                f"[VectorIndexComponents] {name} missing methods {missing} "
                f"(got {type(store).__name__})"
            )

    # ==========================================================
    # VALIDATION
    # ==========================================================

    async def shutdown(self) -> None:
        """Garante que serviços com background tasks (batching) façam flush."""
        # 1. Varre slots dinamicamente para parar componentes gerenciados
        for field_name in self.__slots__:
            attr = getattr(self, field_name)
            if isinstance(attr, ManagedComponent):
                try:
                    await attr.stop()
                    logger.debug(f"Component {field_name} stopped")
                except Exception:
                    logger.exception(f"Failed to stop {field_name} during shutdown")

        # 2. Aguarda ou cancela tarefas de inicialização pendentes
        if self._background_tasks:
            for task in self._background_tasks:
                if not task.done():
                    task.cancel()

            await asyncio.gather(*self._background_tasks, return_exceptions=True)
            self._background_tasks.clear()

        # 2. Limpeza de memória de estruturas pesadas
        for name, attr in [
            ("temporal_index", self.temporal_index),
            ("causal_graph", self.causal_graph),
        ]:
            try:
                if attr and hasattr(attr, "clear"):
                    attr.clear()
            except Exception:
                logger.error(f"Failed to clear {name} during shutdown")

    def validate(self) -> None:
        """
        Garante integridade estrutural dos componentes.
        """

        # -----------------------------------------------------
        # STORES (duck typing)
        # -----------------------------------------------------

        self._validate_store(self.vector_reader, self.READER_METHODS, "vector_reader")
        self._validate_store(self.vector_writer, self.WRITER_METHODS, "vector_writer")
        self._validate_store(self.document_store, self.KV_METHODS, "document_store")
        self._validate_store(self.token_store, self.KV_METHODS, "token_store")
        self._validate_store(self.metadata_store, self.KV_METHODS, "metadata_store")

        # -----------------------------------------------------
        # RANKING
        # -----------------------------------------------------

        assert isinstance(self.stage1_ranker, Ranker), "Invalid stage1_ranker"
        assert isinstance(self.stage2_ranker, Ranker), "Invalid stage2_ranker"
        assert isinstance(self.final_ranker, Ranker), "Invalid final_ranker"

        # -----------------------------------------------------
        # CLASSIFIER
        # -----------------------------------------------------

        assert isinstance(self.query_classifier, QueryClassifier), "Invalid query_classifier"

        # -----------------------------------------------------
        # ANN
        # -----------------------------------------------------

        assert isinstance(self.ivf_builder, IVFBuilder), "Invalid ivf_builder"
        assert isinstance(self.ivf_router, IVFRouter), "Invalid ivf_router"

        # -----------------------------------------------------
        # CLUSTERING
        # -----------------------------------------------------

        assert isinstance(self.cluster_manager, ClusterManager), "Invalid cluster_manager"

        if self.cluster_router is not None:
            assert isinstance(self.cluster_router, ClusterRouter), (
                f"Invalid cluster_router: {type(self.cluster_router)}"
            )
