from typing import Any


class TemporalExpansion:
    priority = 15

    def __init__(self, temporal_index: Any = None) -> None:
        self.temporal = temporal_index

    async def run(self, ctx: Any) -> Any:
        if not self.temporal or not ctx.candidates:
            return ctx

        expanded = set(ctx.candidates)

        for doc_id in ctx.candidates:
            chain = self.temporal.causal_chain(doc_id, depth=1)
            expanded.update(chain)

        ctx.candidates = list(expanded)

        return ctx
