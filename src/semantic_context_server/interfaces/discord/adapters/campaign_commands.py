from typing import Any

from discord import app_commands
from discord.ext.commands import Context

from semantic_context_server.application.commands.campaign.command import (
    CampaignCommand,
)


def register_campaign_commands(bot: Any, command_bus: Any) -> Any:
    @bot.hybrid_command(
        name="campaign",
        description="Gerenciar campanhas: start, switch, list, delete, stop",
    )
    @app_commands.choices(
        action=[
            app_commands.Choice(name="Start (criar/iniciar)", value="start"),
            app_commands.Choice(name="Switch (trocar)", value="switch"),
            app_commands.Choice(name="List", value="list"),
            app_commands.Choice(name="Delete", value="delete"),
            app_commands.Choice(name="Stop", value="stop"),
        ]
    )
    async def campaign(
        ctx: Context,
        action: str | None = None,
        name: str | None = None,
    ) -> Any:
        await ctx.defer()

        # Define ação padrão como status
        action = action or "status"

        # Validação de nome para criação
        if action == "start" and not name:
            return await ctx.send("⚠️ Você precisa informar um nome para a campanha.")

        # Validação de campanha ativa para encerramento
        if action == "stop":
            deps = getattr(bot, "deps", None)
            active_id = deps.campaign_state.get(ctx.channel.id) if deps else None
            if not active_id:
                return await ctx.send("⚠️ Não há nenhuma campanha ativa neste canal.")

        command = CampaignCommand(
            action=action,
            name=name,
            user_id=str(ctx.author.id),
        )

        result = await command_bus.dispatch(ctx, command)

        await ctx.send(result)

    return campaign
