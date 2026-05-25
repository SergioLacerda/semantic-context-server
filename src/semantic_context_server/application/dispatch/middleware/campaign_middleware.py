from collections.abc import Awaitable, Callable
from typing import Any


async def campaign_middleware(command: Any, ctx: Any, next: Callable[[], Awaitable[Any]]) -> Any:
    # ======================================================
    # RESOLVE DEPENDENCIES
    # ======================================================
    deps = getattr(ctx, "bot", None)

    if not deps:
        return await next()

    deps = ctx.bot.deps

    # ======================================================
    # RESOLVE CAMPAIGN FROM STATE
    # ======================================================
    campaign_id = deps.campaign_state.get(ctx.channel.id)

    if campaign_id:
        ctx.campaign_id = campaign_id
        ctx.campaign = await deps.resolve_campaign(campaign_id)

    return await next()
