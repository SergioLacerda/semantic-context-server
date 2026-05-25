from typing import Any


class ClusterDedupStage:
    priority = 76

    def __init__(self, cluster_router: Any) -> None:
        self.router = cluster_router

    async def run(self, ctx: Any) -> Any:
        if not ctx.candidates:
            return ctx

        ctx.candidates = self.router.route(ctx.candidates)

        return ctx
