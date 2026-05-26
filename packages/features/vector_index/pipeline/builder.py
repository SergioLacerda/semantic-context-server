from typing import Any

from packages.features.vector_index.pipeline.pipeline import RetrievalPipeline

# pipeline stages
from packages.features.vector_index.pipeline.stages import (
    AdaptiveCandidateLimiter,
    AdaptiveRankingStage,
    ANNPrefilter,
    CandidateRetriever,
    CandidateSetReservoir,
    CausalExpansion,
    ClusterDedupStage,
    DeduplicateStage,
    EmbedStage,
    HybridFusionStage,
    NarrativeImportanceStage,
    QueryExpansion,
    RankingStage1,
    RankingStage2,
    ResetEmbeddingStage,
    TemporalExpansion,
    TemporalPriorityStage,
    TimelineExpansion,
)
from packages.features.vector_index.pipeline.stages.ranking_final_stage import (
    RankingFinalStage,
)

# ranking
from packages.features.vector_index.ranking.stage1_ranker import Stage1Ranker


class PipelineBuilder:
    def __init__(self, deps: Any) -> None:
        self.deps = deps

    def build(self) -> RetrievalPipeline:
        stages = [
            # =================================================
            # 🔍 QUERY PREPARATION
            # =================================================
            QueryExpansion(self.deps.memory_provider),
            ResetEmbeddingStage(),
            # 🔥 obrigatório antes de retrieval
            EmbedStage(self.deps.embedding_fn),
            # =================================================
            # 🔎 RETRIEVAL
            # =================================================
            ANNPrefilter(ann=self.deps.ann),
            CandidateRetriever(
                embedding_fn=self.deps.embedding_fn,
            ),
            # =================================================
            # 🧠 NARRATIVE EXPANSION
            # =================================================
            CausalExpansion(self.deps.causal_graph),
            TemporalExpansion(self.deps.temporal_index),
            TimelineExpansion(self.deps.temporal_index),
            # =================================================
            # 🎛️ CANDIDATE CONTROL
            # =================================================
            CandidateSetReservoir(),
            AdaptiveCandidateLimiter(),
            # =================================================
            # 🧭 CONTEXT PRIORITIZATION
            # =================================================
            TemporalPriorityStage(),
            *([ClusterDedupStage(self.deps.cluster_router)] if self.deps.cluster_router else []),
            DeduplicateStage(),
            # =================================================
            # 🧮 RANKING PIPELINE (🔥 CORE)
            # =================================================
            # 🔹 Stage 1 → recall leve (rápido)
            RankingStage1(ranker=Stage1Ranker()),
            # 🔹 Stage 2 → refinamento (temporal + cluster + lexical)
            RankingStage2(),
            # 🔹 Fusion → combina múltiplos sinais (RRF)
            HybridFusionStage(),
            # 🔹 Adaptive → ajusta dinamicamente baseado no contexto
            AdaptiveRankingStage(),
            # 🔹 Narrative → prioriza coerência da história
            NarrativeImportanceStage(self.deps.importance),
            # 🔹 Final → corta top_k e score final
            RankingFinalStage(),
        ]

        return RetrievalPipeline(stages)
