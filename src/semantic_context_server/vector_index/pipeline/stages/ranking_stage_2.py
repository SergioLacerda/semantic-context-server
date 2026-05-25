from typing import Any

from semantic_context_server.vector_index.ranking.stage2_ranker import Stage2Ranker


class RankingStage2:
    def __init__(self) -> None:
        self.ranker = Stage2Ranker()

    async def run(self, ctx: Any) -> Any:
        candidates = ctx.candidates

        ranked = await self.ranker.rank(ctx, candidates)

        ctx.stage2_candidates = ranked
        ctx.candidates = ranked

        return ctx
