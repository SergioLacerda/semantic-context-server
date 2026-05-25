from typing import Any

from semantic_context_server.vector_index.ranking.hybrid_ranker import HybridRanker


class HybridFusionStage:
    priority = 100
    min_candidates = 1

    def __init__(self, ranker: Any = None) -> None:
        self.ranker = ranker or HybridRanker()

    async def run(self, ctx: Any) -> Any:
        if not ctx.candidates:
            return ctx

        sources, weights = [ctx.candidates], [1.0]
        self._add_lexical(ctx, sources, weights)
        self._add_causal(ctx, sources, weights)
        self._add_timeline(ctx, sources, weights)
        self._add_memory_layers(ctx, sources, weights)

        sources = [list(dict.fromkeys(src)) for src in sources]
        ctx.candidates = self.ranker.fuse(*sources, weights=weights)
        return ctx

    def _add_lexical(self, ctx: Any, sources: list[Any], weights: list[float]) -> None:
        lexical = getattr(ctx, "lexical_results", None)
        if lexical:
            sources.append(lexical)
            weights.append(0.8)

    def _add_causal(self, ctx: Any, sources: list[Any], weights: list[float]) -> None:
        causal_graph = getattr(ctx, "causal_graph", None)
        if not causal_graph:
            return
        causal = causal_graph.expand(ctx.candidates, depth=2)
        if causal:
            sources.append(causal)
            weights.append(0.7)

    def _add_timeline(self, ctx: Any, sources: list[Any], weights: list[float]) -> None:
        temporal = getattr(ctx, "temporal_index", None)
        if not temporal:
            return
        timeline: list[Any] = []
        for doc_id in ctx.candidates:
            timeline.extend(temporal.causal_chain(doc_id, depth=2))
        if timeline:
            sources.append(timeline)
            weights.append(0.6)

    def _add_memory_layers(self, ctx: Any, sources: list[Any], weights: list[float]) -> None:
        memory_layers = getattr(ctx, "memory_layers", None)
        if not memory_layers:
            return
        memory = [doc for layer in memory_layers for doc in (layer.search(ctx.q_vec) or [])]
        if memory:
            sources.append(memory)
            weights.append(0.9)
