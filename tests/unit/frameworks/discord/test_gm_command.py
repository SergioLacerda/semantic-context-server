import pytest

from semantic_context_server.frameworks.discord.adapters.gm_commands import (
    register_gm_commands,
)
from tests.config.factories.framework.bot import make_bot
from tests.config.factories.framework.context import make_context
from tests.config.factories.framework.deps import make_deps
from tests.config.fakes.application.usecases.fake_usecases import DummyNarrative

# ---------------------------------------------------------
# SUCCESS
# ---------------------------------------------------------


@pytest.mark.asyncio
async def test_gm_command_success():
    ctx = make_context(guild_id=None, user_id="999")

    ctx.campaign_id = "c1"

    deps = make_deps(narrative=DummyNarrative(result="Ataque realizado"))
    bot = make_bot(deps=deps)

    register_gm_commands(bot, bot.bus)

    await bot._command(ctx, action="attack")

    assert ctx.sent_messages
    assert ctx.sent_messages[0] != ""


# ---------------------------------------------------------
# EMPTY INPUT
# ---------------------------------------------------------


@pytest.mark.asyncio
async def test_gm_empty_action():
    ctx = make_context(guild_id=None, user_id="999")

    ctx.campaign_id = "c1"

    deps = make_deps(narrative=DummyNarrative())
    bot = make_bot(deps=deps)

    register_gm_commands(bot, bot.bus)

    await bot._command(ctx, action="")

    assert ctx.sent_messages
    assert "⚠️" in ctx.sent_messages[0]


# ---------------------------------------------------------
# NO RESPONSE (Response vazio)
# ---------------------------------------------------------


@pytest.mark.asyncio
async def test_gm_no_response():
    ctx = make_context(guild_id=None, user_id="999")

    ctx.campaign_id = "c1"

    deps = make_deps(narrative=DummyNarrative(result=""))
    bot = make_bot(deps=deps)

    register_gm_commands(bot, bot.bus)

    await bot._command(ctx, action="attack")

    assert ctx.sent_messages
    assert "⚠️" in ctx.sent_messages[0]


# ---------------------------------------------------------
# EXCEPTION
# ---------------------------------------------------------


@pytest.mark.asyncio
async def test_gm_exception():
    ctx = make_context(guild_id=None, user_id="999")

    ctx.campaign_id = "c1"

    deps = make_deps(narrative=DummyNarrative(error=RuntimeError("boom")))
    bot = make_bot(deps=deps)

    deps.campaign_state.set(ctx.channel.id, "test_campaign")

    register_gm_commands(bot, bot.bus)

    with pytest.raises(RuntimeError):
        await bot._command(ctx, action="attack")
