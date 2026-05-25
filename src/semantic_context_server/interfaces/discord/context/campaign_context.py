from typing import Any

from semantic_context_server.interfaces.discord.utils.ids import get_campaign_id


def resolve_campaign_id(ctx: Any, campaign_state: Any) -> str:
    channel_id = str(ctx.channel.id)

    campaign = campaign_state.get(channel_id)

    if campaign:
        return str(campaign)

    return get_campaign_id(ctx)
