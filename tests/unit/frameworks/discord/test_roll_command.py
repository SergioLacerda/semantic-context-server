import pytest

from semantic_context_server.interfaces.discord.adapters.roll_commands import (
    register_roll_command,
)
from tests.config.factories.framework.bot import make_bot
from tests.config.factories.framework.context import make_context
from tests.config.factories.framework.deps import make_deps
from tests.config.fakes.application.usecases.fake_usecases import DummyRoll

# ---------------------------------------------------------
# SUCCESS
# ---------------------------------------------------------


@pytest.mark.asyncio
async def test_roll_success():
    ctx = make_context(guild_id=None, user_id="999")

    # Garante que o contexto tenha um campaign_id para o adaptador
    ctx.campaign_id = "c1"

    deps = make_deps(roll_dice=DummyRoll(result="resultado"))
    bot = make_bot(deps=deps)

    # O adaptador agora recebe apenas bot e command_bus
    register_roll_command(bot, bot.bus)

    await bot._command(ctx, expression="1d20")

    assert ctx.sent_messages


# ---------------------------------------------------------
# EMPTY EXPRESSION
# ---------------------------------------------------------


@pytest.mark.asyncio
async def test_roll_empty_expression():
    ctx = make_context(guild_id=None, user_id="999")

    deps = make_deps(roll_dice=DummyRoll())
    bot = make_bot(deps=deps)

    register_roll_command(bot, bot.bus)

    await bot._command(ctx, expression="")

    assert ctx.sent_messages
    assert ctx.sent_messages[0] != ""


# ---------------------------------------------------------
# NO RESULT
# ---------------------------------------------------------


@pytest.mark.asyncio
async def test_roll_no_result():
    ctx = make_context(guild_id=None, user_id="999")

    ctx.campaign_id = "c1"

    deps = make_deps(roll_dice=DummyRoll(result=None))  # type: ignore
    bot = make_bot(deps=deps)

    register_roll_command(bot, bot.bus)

    await bot._command(ctx, expression="1d20")

    assert ctx.sent_messages
    assert "⚠️" in ctx.sent_messages[0]
