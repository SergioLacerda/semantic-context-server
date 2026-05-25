from typing import Any


class TimelineExpansion:
    priority = 16

    def __init__(self, temporal_index: Any = None) -> None:
        self.temporal = temporal_index

    async def run(self, ctx: Any) -> Any:
        if not self.temporal or not ctx.candidates:
            return ctx

        expanded: list[Any] = []

        for doc_id in ctx.candidates:
            expanded.append(doc_id)

            neighbors = self.temporal.causal_chain(doc_id, depth=2)

            expanded.extend(neighbors)

        # dedupe mantendo ordem
        ctx.candidates = list(dict.fromkeys(expanded))

        return ctx
