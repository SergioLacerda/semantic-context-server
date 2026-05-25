from typing import Any


class AdaptiveCandidateLimiter:
    priority = 60

    async def run(self, ctx: Any) -> Any:
        k = getattr(ctx, "k", 10)

        if ctx.candidates:
            ctx.candidates = ctx.candidates[: k * 5]

        return ctx
