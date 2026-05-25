from typing import Any

from .campaign_commands import register_campaign_commands
from .gm_commands import register_gm_commands
from .roll_commands import register_roll_command
from .session_commands import register_session_commands

# ==========================================================
# PUBLIC API
# ==========================================================

__all__ = [
    "register_gm_commands",
    "register_gm_command",
    "register_roll_command",
    "register_session_commands",
    "register_all_commands",
]


# ==========================================================
# AGGREGATOR (🔥 RECOMENDADO)
# ==========================================================


def register_all_commands(bot: Any, command_bus: Any) -> None:
    """
    Registra todos os comandos Discord no bot.
    """

    register_campaign_commands(bot, command_bus)
    register_gm_commands(bot, command_bus)
    register_roll_command(bot, command_bus)
    register_session_commands(bot, command_bus)
