from typing import Any


class TemporalPriorityStage:
    priority = 70

    async def run(self, ctx: Any) -> Any:
        if not ctx.candidates or not ctx.temporal_index:
            return ctx

        scored: list[tuple[float, Any]] = []

        for doc_id in ctx.candidates:
            score = ctx.temporal_index.recency_score(doc_id)
            scored.append((score, doc_id))

        scored.sort(reverse=True)

        ctx.candidates = [doc_id for _, doc_id in scored]

        return ctx
