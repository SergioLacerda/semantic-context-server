from typing import Any

from discord.ext.commands import Context

from semantic_context_server.application.commands.roll.command import RollCommand


def register_roll_command(bot: Any, command_bus: Any) -> Any:
    @bot.hybrid_command(
        name="roll",
        description="Rola dados (ex: 1d20, 2d6+3)",
    )
    async def roll(ctx: Context, expression: str) -> Any:
        await ctx.defer()

        expression = (expression or "").strip()

        if not expression:
            return await ctx.send("⚠️ Informe uma expressão válida (ex: 1d20).")

        # ======================================================
        # RESOLVE CAMPAIGN
        # ======================================================
        campaign_id = getattr(ctx, "campaign_id", None)

        if not campaign_id:
            return await ctx.send("⚠️ Nenhuma campanha ativa.")

        command = RollCommand(
            campaign_id=campaign_id,
            expression=expression,
            user_id=ctx.author.id,
        )

        result = await command_bus.dispatch(ctx, command)
        text = getattr(result, "text", result)
        text = str(text or "").strip()
        if not text:
            return await ctx.send("⚠️ Erro ao executar rolagem.")

        # 🔥 safe send após defer
        if hasattr(ctx, "interaction") and ctx.interaction:
            await ctx.interaction.followup.send(text)
        else:
            await ctx.send(text)

    return roll
