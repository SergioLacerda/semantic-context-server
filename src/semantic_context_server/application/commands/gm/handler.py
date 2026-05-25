from typing import Any

from semantic_context_server.application.commands.gm.command import GMCommand


class GMCommandHandler:
    def __init__(self, deps: Any, cache: Any) -> None:
        self.deps = deps
        self.cache = cache

    async def handle(self, command: GMCommand, ctx: Any = None) -> Any:
        if not command.action:
            return "⚠️ Ação inválida."

        if not ctx:
            return "⚠️ Contexto inválido."

        # 🔥 resolve campanha corretamente
        campaign_id = command.campaign_id
        campaign = await self.deps.resolve_campaign(campaign_id)

        result = await campaign.narrative.execute(
            campaign_id=campaign_id,
            action=command.action,
            user_id=command.user_id,
        )

        # Invalidação compatível com diferentes interfaces de cache.
        if hasattr(self.cache, "invalidate_prefix"):
            await self.cache.invalidate_prefix(f"campaign:{campaign_id}")
        elif hasattr(self.cache, "delete"):
            await self.cache.delete(f"campaign:{campaign_id}")

        return result
