from tests.config.helpers.discord_factory import make_ctx


def make_context(
    *,
    interaction: bool = False,
    user_id: str = "user1",
    channel_id: str = "channel1",
    guild_id: str | None = "guild1",
):
    ctx = make_ctx(interaction=interaction)

    # ---------------------------------------
    # OVERRIDES
    # ---------------------------------------
    ctx.author.id = user_id
    ctx.channel.id = channel_id

    if guild_id is None:
        ctx.guild = None  # type: ignore
    else:
        ctx.guild.id = guild_id

    return ctx
