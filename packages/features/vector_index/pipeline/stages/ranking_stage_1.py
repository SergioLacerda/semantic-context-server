from typing import Any


class RankingStage1:
    def __init__(self, ranker: Any) -> None:
        self.ranker = ranker

    async def run(self, ctx: Any) -> Any:
        candidates = ctx.candidates

        ranked = await self.ranker.rank(ctx, candidates)

        ctx.stage1_candidates = ranked
        ctx.candidates = ranked

        return ctx
