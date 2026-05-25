from typing import Any

from semantic_context_server.application.queries.list_campaigns_query import (
    ListCampaignsQuery,
)


class CampaignCommandHandler:
    def __init__(self, deps: Any, query_bus: Any, cache: Any) -> None:
        self.deps = deps
        self.query_bus = query_bus
        self.cache = cache

    async def handle(self, command: Any, ctx: Any = None) -> str:
        if not ctx:
            return "⚠️ Contexto inválido."

        state = self.deps.campaign_state
        channel_id = ctx.channel.id

        # ======================================================
        # LIST
        # ======================================================
        if command.action == "list":
            result: str = await self.query_bus.dispatch(
                ListCampaignsQuery(),
                ctx=ctx,
            )
            return result

        # ======================================================
        # START
        # ======================================================
        if command.action == "start":
            await self.deps.create_campaign.execute(command.name)

            state.set(channel_id, command.name)

            await self.cache.delete(f"campaigns:{channel_id}")

            return f"🎲 Campanha '{command.name}' iniciada."

        # ======================================================
        # SWITCH
        # ======================================================
        if command.action == "switch":
            state.set(channel_id, command.name)

            return f"🔁 Campanha alterada para '{command.name}'."

        # ======================================================
        # STOP
        # ======================================================
        if command.action == "stop":
            state.clear(channel_id)

            await self.cache.delete(f"campaigns:{channel_id}")

            return "🛑 Campanha encerrada."

        # ======================================================
        # FALLBACK
        # ======================================================
        return "⚠️ Ação inválida."
