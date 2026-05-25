import logging

from discord.ext.commands import Context

logger = logging.getLogger("semantic_context_server.discord")


def get_campaign_id(ctx: Context) -> str:
    """
    Retorna ID da campanha baseado no contexto:

    - Guild → guild.id
    - DM → dm_<user_id>
    - fallback → unknown_campaign
    """
    guild = getattr(ctx, "guild", None)
    if guild and getattr(guild, "id", None):
        return str(guild.id)

    author = getattr(ctx, "author", None)
    if author and getattr(author, "id", None):
        return f"dm_{author.id}"

    logger.warning("Fallback campaign_id used (ctx=%s)", ctx)

    return "unknown_campaign"


def get_user_id(ctx: Context) -> str:
    """
    Retorna ID do usuário.
    """
    author = getattr(ctx, "author", None)

    if author and getattr(author, "id", None):
        return str(author.id)

    logger.warning("Fallback user_id used (ctx=%s)", ctx)

    return "unknown_user"
