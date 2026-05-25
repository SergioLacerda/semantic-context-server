from typing import Any

from discord.ext.commands import Context

from semantic_context_server.application.commands.session.command import (
    SessionCommand,
)


def register_session_commands(bot: Any, command_bus: Any) -> Any:
    @bot.hybrid_command(
        name="endsession",
        description="Finaliza sessão atual",
    )
    async def endsession(ctx: Context) -> Any:
        await ctx.defer()

        # 🔥 obter campaign_id
        campaign_id = getattr(ctx, "campaign_id", None)

        if not campaign_id:
            return await ctx.send("⚠️ Nenhuma campanha ativa.")

        command = SessionCommand(
            campaign_id=campaign_id,
        )

        try:
            result = await command_bus.dispatch(ctx, command)

            interaction = getattr(ctx, "interaction", None)

            if interaction is not None:
                await interaction.followup.send(result)
            else:
                await ctx.send(result)

        except Exception:
            await ctx.send("⚠️ Erro ao encerrar sessão.")

    return endsession
