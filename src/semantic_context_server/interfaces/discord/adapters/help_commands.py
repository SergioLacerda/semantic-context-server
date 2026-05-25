from typing import Any

from discord.ext.commands import Context


def register_help_commands(bot: Any, command_registry: Any) -> Any:
    @bot.hybrid_command(
        name="commands",
        description="Lista comandos disponíveis",
    )
    async def commands(ctx: Context) -> Any:
        await ctx.defer()

        commands_meta = command_registry.list_meta()

        if not commands_meta:
            return await ctx.send("⚠️ Nenhum comando disponível.")

        lines = ["📚 **Comandos disponíveis:**\n"]

        current_category = None

        for cmd in commands_meta:
            category = cmd.get("category", "Outros")

            if category != current_category:
                current_category = category
                lines.append(f"\n{category}\n")

            usage = cmd.get("usage", cmd["name"])
            description = cmd.get("description", "")

            lines.append(f"{usage} — {description}")

        await ctx.send("\n".join(lines))

    return commands
