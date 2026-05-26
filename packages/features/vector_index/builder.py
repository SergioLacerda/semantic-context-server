import asyncio
import logging
from typing import Any

from packages.features.vector_index.adapter import VectorIndexAdapter

# ANN
from packages.features.vector_index.ann.ivf_builder import IVFBuilder
from packages.features.vector_index.ann.ivf_router import IVFRouter

# classifier
from packages.features.vector_index.classifiers.default_query_classifier import (
    DefaultQueryClassifier,
)

# clustering
from packages.features.vector_index.clustering.cluster_builder import ClusterBuilder
from packages.features.vector_index.clustering.cluster_manager import ClusterManager
from packages.features.vector_index.clustering.cluster_simple_router import (
    SimpleClusterRouter,
)

# components
from packages.features.vector_index.components import ManagedComponent, VectorIndexComponents
from packages.features.vector_index.core.vector_index import VectorIndex

# narrativa
from packages.features.vector_index.narrative.causality_graph import CausalityGraph
from packages.features.vector_index.narrative.timeline_index import TimelineIndex
from packages.features.vector_index.ranking.ranking_final import RankingFinal

# ranking
from packages.features.vector_index.ranking.stage1_ranker import Stage1Ranker
from packages.features.vector_index.ranking.stage2_ranker import Stage2Ranker
from packages.features.vector_index.runtime.deduplicator import InflightDeduplicator

logger = logging.getLogger("semantic_context_server.vector_index.builder")


class VectorIndexBuilder:
    """
    Builder responsável por compor o VectorIndex.

    ✔ Core 100% síncrono
    ✔ Sem dependência de runtime
    ✔ Validação de contratos
    ✔ Inicialização segura
    """

    def __init__(
        self,
        embedding_service: Any,
        storage_backend: Any,
        tokenizer: Any,
        executor: Any,
        memory_provider: Any = None,
        entity_provider: Any = None,
        context_provider: Any = None,
        query_classifier: Any = None,
    ) -> None:
        self.executor = executor
        self.embedding = embedding_service
        self.storage = storage_backend
        self.tokenizer = tokenizer

        self.memory_provider = memory_provider
        self.entity_provider = entity_provider
        self.context_provider = context_provider

        self.query_classifier = query_classifier or DefaultQueryClassifier()

    # ==========================================================
    # STORES
    # ==========================================================

    def _build_stores(self) -> dict[str, Any]:
        raw_vector_store = self.storage.build_vector_store()
        # O batching técnico é removido aqui pois o VectorWriterService (Application)
        # já gerencia o acúmulo de escrita de forma mais eficiente (Business Batching).
        return {
            "vector_reader": raw_vector_store,
            "vector_writer": raw_vector_store,  # Comunicação direta com o Adaptador
            "document_store": self.storage.build_document_store(),
            "token_store": self.storage.build_token_store(),
            "metadata_store": self.storage.build_metadata_store(),
        }

    # ==========================================================
    # ANN
    # ==========================================================

    def _build_ann(self) -> tuple[IVFBuilder, IVFRouter]:
        return IVFBuilder(self.executor), IVFRouter()

    async def _initialize_ann(self, components: Any) -> None:
        vector_reader = components.vector_reader

        if not hasattr(vector_reader, "keys"):
            return

        # Coleta de chaves pode ser lenta em adaptadores JSON (I/O bloqueante)
        # Despachamos para o executor se for um método síncrono
        doc_ids = await self.executor.run(vector_reader.keys)
        if not doc_ids:
            return

        logger.info("Building ANN index", extra={"docs": len(doc_ids)})

        # Nota: IVFBuilder ainda utiliza o port completo para construção inicial
        ivf_index = await components.ivf_builder.build(doc_ids, vector_reader)

        if ivf_index:
            components.ivf_router.set_index(ivf_index)

    # ==========================================================
    # CLUSTERING
    # ==========================================================

    def _build_clustering(
        self,
    ) -> tuple[ClusterBuilder, ClusterManager, SimpleClusterRouter]:
        cluster_builder = ClusterBuilder()
        cluster_manager = ClusterManager(cluster_builder, self.executor)
        cluster_router = SimpleClusterRouter(cluster_manager)

        return cluster_builder, cluster_manager, cluster_router

    async def _initialize_clusters(self, components: Any) -> None:
        vector_reader = components.vector_reader

        if not hasattr(vector_reader, "keys"):
            return

        # Garantindo que a leitura de chaves não bloqueie o event loop
        doc_ids = await self.executor.run(vector_reader.keys)
        if not doc_ids:
            return

        logger.info("Building clusters", extra={"docs": len(doc_ids)})

        await components.cluster_manager.update(doc_ids, vector_reader)

    # ==========================================================
    # NARRATIVE
    # ==========================================================

    def _build_narrative(self) -> tuple[TimelineIndex, CausalityGraph]:
        return TimelineIndex(), CausalityGraph()

    # ==========================================================
    # COMPONENTS
    # ==========================================================

    def _build_components(self, stores: dict[str, Any]) -> VectorIndexComponents:
        ivf_builder, ivf_router = self._build_ann()
        cluster_builder, cluster_manager, cluster_router = self._build_clustering()
        temporal_index, causal_graph = self._build_narrative()

        # Deduplicador para operações custosas (embeddings, etc)
        # Utiliza o executor da aplicação para cumprir o Async Mandate
        deduplicator = InflightDeduplicator(self.executor)

        components = VectorIndexComponents(
            query_classifier=self.query_classifier,
            stage1_ranker=Stage1Ranker(top_k=120),
            stage2_ranker=Stage2Ranker(top_k=60, executor=self.executor),
            final_ranker=RankingFinal(executor=self.executor, top_k=4),
            cluster_manager=cluster_manager,
            executor=self.executor,
            deduplicator=deduplicator,
            vector_reader=stores["vector_reader"],
            vector_writer=stores["vector_writer"],
            document_store=stores["document_store"],
            token_store=stores["token_store"],
            metadata_store=stores["metadata_store"],
            ivf_builder=ivf_builder,
            ivf_router=ivf_router,
            temporal_index=temporal_index,
            causal_graph=causal_graph,
        )

        cluster_router = SimpleClusterRouter(cluster_manager)
        components.cluster_router = cluster_router
        components.validate()

        return components

    # ==========================================================
    # ENGINE
    # ==========================================================

    def _build_engine(
        self,
        components: VectorIndexComponents,
        semantic_cache: Any,
        campaign_id: str | None,
    ) -> VectorIndex:
        return VectorIndex(
            components=components,
            embedding_service=self.embedding,
            tokenizer=self.tokenizer,
            memory_provider=self.memory_provider,
            entity_provider=self.entity_provider,
            context_provider=self.context_provider,
            semantic_cache=semantic_cache,
            campaign_id=campaign_id,
        )

    # ==========================================================
    # INITIALIZATION
    # ==========================================================

    async def _initialize_all(self, components: VectorIndexComponents) -> None:
        try:
            await self._initialize_ann(components)
            await self._initialize_clusters(components)
        except Exception:
            logger.exception("VectorIndex background initialization failed")

    # ==========================================================
    # PUBLIC BUILD
    # ==========================================================

    def build(
        self,
        *,
        semantic_cache: Any = None,
        campaign_id: str | None = None,
        initialize: bool = True,
        init_timeout: float = 30.0,
    ) -> VectorIndexAdapter:
        logger.info(
            "Building VectorIndex",
            extra={"campaign_id": campaign_id or "global"},
        )

        # 1. stores
        stores = self._build_stores()

        # 2. components
        components = self._build_components(stores)

        # 3. engine
        engine = self._build_engine(components, semantic_cache, campaign_id)

        # 4. Agendar inicialização e tracking de lifecycle
        # O motor inicia de forma transparente; buscas iniciais serão lineares
        # até que o índice ANN (IVF/Clusters) esteja pronto.
        if initialize:
            init_task = asyncio.create_task(self._initialize_all(components))
            components._background_tasks.append(init_task)

        if isinstance(components.vector_writer, ManagedComponent):
            writer_task = asyncio.create_task(components.vector_writer.start())
            components._background_tasks.append(writer_task)

        # 5. adapter (async boundary externo)
        return VectorIndexAdapter(engine, self.executor)
