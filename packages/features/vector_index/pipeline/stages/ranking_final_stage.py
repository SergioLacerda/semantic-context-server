from typing import Any

from packages.features.vector_index.ranking.ranking_final import RankingFinal


class RankingFinalStage:
    priority = 100

    def __init__(self) -> None:
        self.ranker = RankingFinal()

    async def run(self, ctx: Any) -> Any:
        if not ctx.candidates:
            ctx.results = []
            return ctx

        ctx.results = self.ranker.rank(ctx, ctx.candidates)

        return ctx
