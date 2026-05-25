from typing import Any


class SessionCommandHandler:
    def __init__(self, cache: Any) -> None:
        self.cache = cache

    async def handle(self, command: Any, ctx: Any = None) -> str:
        result = await command.campaign.end_session.execute(command.campaign_id)

        await self.cache.invalidate_prefix(f"campaign:{command.campaign_id}")

        if not result:
            return "⚠️ Nenhum resumo gerado."

        return f"🛑 Sessão encerrada.\n\n{result}"
