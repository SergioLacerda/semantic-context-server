from unittest.mock import AsyncMock

import pytest

from semantic_context_server.interfaces.discord.adapters.campaign_commands import (
    register_campaign_commands,
)
from tests.config.factories.framework.bot import make_bot
from tests.config.factories.framework.context import make_context
from tests.config.factories.framework.deps import make_deps


@pytest.mark.asyncio
async def test_campaign_start_success():
    ctx = make_context()
    deps = make_deps()
    bot = make_bot(deps=deps)
    bot.bus.dispatch = AsyncMock(return_value="🎲 Campanha 'aventura' iniciada.")

    register_campaign_commands(bot, bot.bus)
    await bot._command(ctx, action="start", name="aventura")

    assert ctx.sent_messages
    assert "🎲" in ctx.sent_messages[0]
    assert "aventura" in ctx.sent_messages[0]


@pytest.mark.asyncio
async def test_campaign_start_without_name():
    ctx = make_context()
    deps = make_deps()
    bot = make_bot(deps=deps)

    register_campaign_commands(bot, bot.bus)
    await bot._command(ctx, action="start", name=None)

    assert "⚠️" in ctx.sent_messages[0]


@pytest.mark.asyncio
async def test_campaign_stop_success():
    ctx = make_context()
    deps = make_deps()
    bot = make_bot(deps=deps)
    bot.bus.dispatch = AsyncMock(return_value="🛑 Campanha encerrada.")

    register_campaign_commands(bot, bot.bus)
    deps.campaign_state.set(ctx.channel.id, "aventura")

    await bot._command(ctx, action="stop")

    assert "🛑" in ctx.sent_messages[0]


@pytest.mark.asyncio
async def test_campaign_stop_without_active():
    ctx = make_context()
    deps = make_deps()
    bot = make_bot(deps=deps)
    # Garantir que não há campanha ativa
    deps.campaign_state.set(ctx.channel.id, None)

    register_campaign_commands(bot, bot.bus)
    await bot._command(ctx, action="stop")

    assert "⚠️" in ctx.sent_messages[0]


@pytest.mark.asyncio
async def test_campaign_status_with_active():
    ctx = make_context()
    deps = make_deps()
    bot = make_bot(deps=deps)
    bot.bus.dispatch = AsyncMock(return_value="🎲 Campanha ativa: aventura")

    register_campaign_commands(bot, bot.bus)
    deps.campaign_state.set(ctx.channel.id, "aventura")

    await bot._command(ctx)

    assert ctx.sent_messages
    assert "🎲" in ctx.sent_messages[0]
    assert "aventura" in ctx.sent_messages[0]


@pytest.mark.asyncio
async def test_campaign_status_without_active():
    ctx = make_context()
    deps = make_deps()
    bot = make_bot(deps=deps)
    bot.bus.dispatch = AsyncMock(return_value="⚠️ Nenhuma campanha ativa.")

    register_campaign_commands(bot, bot.bus)
    await bot._command(ctx)

    assert "⚠️" in ctx.sent_messages[0]


@pytest.mark.asyncio
async def test_campaign_unknown_action():
    ctx = make_context()
    deps = make_deps()
    bot = make_bot(deps=deps)
    bot.bus.dispatch = AsyncMock(return_value="⚠️ Ação inválida.")

    register_campaign_commands(bot, bot.bus)
    await bot._command(ctx, action="invalid")

    assert "⚠️" in ctx.sent_messages[0]


@pytest.mark.asyncio
async def test_start_created():
    ctx = make_context()
    bot = make_bot()

    register_campaign_commands(bot, bot.bus)
    await bot._command(ctx, action="start", name="A")

    assert ctx.sent_messages
    assert "🎲" in ctx.sent_messages[0]


@pytest.mark.asyncio
async def test_start_existing():
    ctx = make_context()
    bot = make_bot()

    register_campaign_commands(bot, bot.bus)
    await bot._command(ctx, action="start", name="A")

    assert ctx.sent_messages


@pytest.mark.asyncio
async def test_list_empty():
    ctx = make_context()
    deps = make_deps(list_campaigns=AsyncMock(return_value=[]))
    bot = make_bot(deps=deps)

    register_campaign_commands(bot, bot.bus)
    await bot._command(ctx, action="list")

    assert "Nenhuma campanha" in ctx.sent_messages[0]


@pytest.mark.asyncio
async def test_list_with_campaigns():
    ctx = make_context()
    deps = make_deps(list_campaigns=AsyncMock(return_value=["Aventura 1"]))
    bot = make_bot(deps=deps)

    register_campaign_commands(bot, bot.bus)
    await bot._command(ctx, action="list")

    assert ctx.sent_messages


@pytest.mark.asyncio
async def test_delete_success():
    ctx = make_context()
    bot = make_bot()

    register_campaign_commands(bot, bot.bus)
    await bot._command(ctx, action="delete", name="A")

    assert ctx.sent_messages


@pytest.mark.asyncio
async def test_delete_not_found():
    ctx = make_context()
    bot = make_bot()

    register_campaign_commands(bot, bot.bus)
    await bot._command(ctx, action="delete", name="A")

    assert ctx.sent_messages
