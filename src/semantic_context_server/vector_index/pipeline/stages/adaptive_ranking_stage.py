from typing import Any

from semantic_context_server.vector_index.runtime.lazy_similarity import (
    LazyVectorSimilarity,
)


class AdaptiveRankingStage:
    """
    Ranking adaptativo baseado no tipo de query.
    """

    priority = 95
    min_candidates = 1

    def __init__(self, top_k: int = 20) -> None:
        self.top_k = top_k

        # perfis de peso
        self.profiles: dict[str, tuple[float, float, float]] = {
            "semantic": (0.7, 0.2, 0.1),
            "memory": (0.4, 0.4, 0.2),
            "lore": (0.5, 0.3, 0.2),
            "investigation": (0.3, 0.5, 0.2),
        }

    # ---------------------------------------------------------
    # PIPELINE ENTRY
    # ---------------------------------------------------------

    async def run(self, ctx: Any) -> Any:
        candidates = ctx.candidates

        if not candidates:
            return ctx

        query_type = getattr(ctx, "query_type", "semantic")

        w_vec, w_lex, w_temp = self.profiles.get(query_type, self.profiles["semantic"])

        # 🔥 cache por contexto
        if not hasattr(ctx, "_lazy_similarity"):
            ctx._lazy_similarity = LazyVectorSimilarity(ctx.vector_store)

        lazy = ctx._lazy_similarity

        query_tokens = set(getattr(ctx, "query_tokens", []) or [])
        get_tokens = getattr(ctx, "get_tokens", None)
        temporal = getattr(ctx, "temporal_index", None)

        scored: list[tuple[float, Any]] = []

        for doc_id in candidates:
            # -----------------------------------------------------
            # vector score (robusto)
            # -----------------------------------------------------
            try:
                vec_score = lazy.similarity(ctx.q_vec, doc_id)
            except Exception:
                vec_score = 0.0

            # -----------------------------------------------------
            # lexical score (robusto)
            # -----------------------------------------------------
            tokens = get_tokens(doc_id) if get_tokens else []
            tokens = set(tokens or [])

            lex_score = len(query_tokens & tokens)

            # -----------------------------------------------------
            # temporal score
            # -----------------------------------------------------
            temp_score = 0.0
            if temporal:
                try:
                    temp_score = temporal.recency_score(doc_id)
                except Exception:
                    temp_score = 0.0

            # -----------------------------------------------------
            # final score
            # -----------------------------------------------------
            final = w_vec * vec_score + w_lex * lex_score + w_temp * temp_score

            scored.append((final, doc_id))

        scored.sort(reverse=True)

        ranked = [doc_id for _, doc_id in scored[: self.top_k]]

        # 🔥 salvar no contexto (debug + observabilidade)
        ctx.adaptive_candidates = ranked

        # 🔥 atualizar pipeline
        ctx.candidates = ranked

        return ctx
