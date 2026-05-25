import contextlib
from typing import Any


class NarrativeImportanceStage:
    priority = 105

    def __init__(self, importance_model: Any = None) -> None:
        self.importance = importance_model

    async def run(self, ctx: Any) -> Any:
        if not ctx.candidates:
            ctx.results = []
            return ctx

        # fallback simples
        ctx.results = ctx.candidates[: getattr(ctx, "k", 4)]

        # se tiver modelo de importância
        if self.importance:
            with contextlib.suppress(Exception):
                ctx.results = self.importance.rank(ctx, ctx.candidates)

        return ctx
