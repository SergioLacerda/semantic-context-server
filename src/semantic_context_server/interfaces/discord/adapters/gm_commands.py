from typing import Any

from discord.ext.commands import Context

from semantic_context_server.application.commands.gm.command import GMCommand


def register_gm_commands(bot: Any, command_bus: Any) -> Any:
    @bot.hybrid_command(
        name="gm",
        description="Executa ação narrativa (ex: atacar goblin, investigar sala)",
    )
    async def gm(ctx: Context, *, action: str) -> Any:
        await ctx.defer()

        # ======================================================
        # RESOLVE CAMPAIGN
        # ======================================================
        campaign_id = getattr(ctx, "campaign_id", None)

        if not campaign_id:
            return await ctx.send("⚠️ Nenhuma campanha ativa.")

        action = (action or "").strip()

        if not action:
            return await ctx.send("⚠️ Ação inválida.")

        # ======================================================
        # BUILD COMMAND (DTO)
        # ======================================================
        command = GMCommand(
            campaign_id=campaign_id,
            user_id=str(ctx.author.id),
            action=action,
        )

        # ======================================================
        # EXECUTION
        # ======================================================
        result = await command_bus.dispatch(ctx, command)
        text = getattr(result, "text", result)
        text = str(text or "").strip()

        if not text:
            return await ctx.send("⚠️ Sem resposta narrativa.")

        interaction = ctx.interaction

        if interaction is not None:
            await interaction.followup.send(text)
        else:
            await ctx.send(text)

    return gm
