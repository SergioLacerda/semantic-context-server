from unittest.mock import MagicMock

import pytest
from discord.ext import commands

from packages.interfaces.discord_bot import create_bot
from tests.config.factories.framework.context import make_context
from tests.config.factories.framework.deps import make_deps
from tests.config.factories.framework.help import make_help
from tests.config.helpers.discord_factory import DummySettings

# ---------------------------------------------------------
# HELPERS
# ---------------------------------------------------------


@pytest.fixture(autouse=True)
def mock_help_command(monkeypatch):
    monkeypatch.setattr(
        "packages.interfaces.discord_bot.bot.register_help_commands",
        lambda bot, registry: make_help(),
    )


def make_test_bot():
    return create_bot(
        settings=DummySettings(),
        deps=make_deps(),
        executor=MagicMock(),
        interaction_state=MagicMock(),
    )


# ---------------------------------------------------------
# BOT CREATION
# ---------------------------------------------------------


@pytest.mark.asyncio
async def test_bot_creation():
    bot = make_test_bot()

    assert bot is not None


# ---------------------------------------------------------
# COOLDOWN ERROR
# ---------------------------------------------------------


@pytest.mark.asyncio
async def test_on_command_error_cooldown():
    bot = make_test_bot()
    ctx = make_context(guild_id=None, user_id="999")

    cooldown = commands.Cooldown(1, 3)
    error = commands.CommandOnCooldown(cooldown, 1.5, commands.BucketType.user)

    await bot.on_command_error(ctx, error)  # type: ignore

    assert ctx.sent_messages
    assert "⏳" in ctx.sent_messages[0]


# ---------------------------------------------------------
# READY SUCCESS
# ---------------------------------------------------------


@pytest.mark.asyncio
async def test_on_ready_sync_called(monkeypatch):
    bot = make_test_bot()

    called = {}

    async def fake_sync(*, guild=None):
        called["ok"] = True
        return []

    monkeypatch.setattr(bot.tree, "sync", fake_sync)

    await bot.on_ready()

    assert called.get("ok") is True


# ---------------------------------------------------------
# READY FAILURE
# ---------------------------------------------------------


@pytest.mark.asyncio
async def test_on_ready_sync_failure(monkeypatch):
    bot = make_test_bot()

    async def fake_sync(*, guild=None):
        raise RuntimeError("fail")

    monkeypatch.setattr(bot.tree, "sync", fake_sync)

    await bot.on_ready()


# ---------------------------------------------------------
# GENERIC ERROR
# ---------------------------------------------------------


@pytest.mark.asyncio
async def test_on_command_error_generic():
    bot = make_test_bot()
    ctx = make_context(guild_id=None, user_id="999")

    await bot.on_command_error(ctx, RuntimeError("boom"))  # type: ignore

    assert ctx.sent_messages
    assert "⚠️" in ctx.sent_messages[0]
