import pytest

from semantic_context_server.frameworks.discord.responder import DiscordResponder
from tests.config.factories.framework.context import make_context


@pytest.mark.asyncio
async def test_send_with_interaction():
    ctx = make_context(interaction=True)

    responder = DiscordResponder(ctx)

    await responder.send("hello")

    assert ctx.sent_messages[0] == "hello"


@pytest.mark.asyncio
async def test_send_fallback():
    ctx = make_context(guild_id=None, user_id="999")

    responder = DiscordResponder(ctx)

    await responder.send("hello")

    assert ctx.sent_messages[0] == "hello"
