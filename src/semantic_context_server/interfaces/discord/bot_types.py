from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from semantic_context_server.interfaces.discord.dependencies import CommandDependencies

from discord.ext import commands


class RPGDiscordBot(commands.Bot):
    deps: CommandDependencies | None

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.deps = None
        self.debug = False
