from typing import Any


class ResetEmbeddingStage:
    priority = 11
    min_candidates = 0

    def run(self, ctx: Any) -> Any:
        current_query = ctx.query

        last_query = getattr(ctx, "_last_query", None)

        if current_query != last_query:
            ctx.q_vec = None
            ctx._last_query = current_query
            ctx.embedding_reset = True

        return ctx
