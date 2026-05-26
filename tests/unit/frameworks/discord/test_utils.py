import pytest

from semantic_context_server.interfaces.discord.utils.ids import (
    get_campaign_id,
    get_user_id,
)
from semantic_context_server.interfaces.discord.utils.messaging import (
    MAX_MESSAGE_LEN,
    send_long_response,
)
from tests.config.factories.framework.context import make_context

# ----------------------------------------
# get_campaign_id
# ----------------------------------------


def test_campaign_id_from_guild():
    ctx = make_context(guild_id="123", user_id="999")

    result = get_campaign_id(ctx)  # type: ignore

    assert result == "123"


def test_campaign_id_dm():
    ctx = make_context(guild_id=None, user_id="999")

    result = get_campaign_id(ctx)  # type: ignore

    assert result == "dm_999"


# ----------------------------------------
# get_user_id
# ----------------------------------------


def test_get_user_id():
    ctx = make_context(guild_id=None, user_id="999")

    assert get_user_id(ctx) == "999"  # type: ignore


# ----------------------------------------
# send_long_response
# ----------------------------------------


@pytest.mark.asyncio
async def test_send_long_response_short():
    ctx = make_context(guild_id=None, user_id="999")

    await send_long_response(ctx, "hello")  # type: ignore

    assert ctx.sent_messages[0] == "hello"


@pytest.mark.asyncio
async def test_send_long_response_long():
    ctx = make_context(guild_id=None, user_id="999")

    long_text = "a" * 5000

    await send_long_response(ctx, long_text)  # type: ignore

    # deve dividir em múltiplas mensagens
    assert len(ctx.sent_messages) > 1


@pytest.mark.asyncio
async def test_send_long_response_with_interaction():
    ctx = make_context(interaction=True)

    await send_long_response(ctx, "hello")  # type: ignore

    assert ctx.sent_messages[0] == "hello"


@pytest.mark.asyncio
async def test_send_long_response_long_interaction():
    ctx = make_context(interaction=True)

    long_text = "a" * 5000

    await send_long_response(ctx, long_text)  # type: ignore

    # múltiplas mensagens
    assert len(ctx.sent_messages) > 1


@pytest.mark.asyncio
async def test_send_long_response_empty():
    ctx = make_context(guild_id=None, user_id="999")

    await send_long_response(ctx, "")  # type: ignore

    assert "Sem conteúdo" in ctx.sent_messages[0]


@pytest.mark.asyncio
async def test_send_long_response_with_header_short():
    ctx = make_context(guild_id=None, user_id="999")

    header = "HEADER: "
    content = "hello"

    await send_long_response(ctx, content, header=header)  # type: ignore

    assert ctx.sent_messages[0] == "HEADER: hello"


@pytest.mark.asyncio
async def test_send_long_response_with_header_long():
    ctx = make_context(guild_id=None, user_id="999")

    header = "HEADER: "
    content = "a" * 5000

    await send_long_response(ctx, content, header=header)  # type: ignore

    # primeiro envia header separado
    assert ctx.sent_messages[0] == header

    # depois envia chunks
    assert len(ctx.sent_messages) > 1


@pytest.mark.asyncio
async def test_chunk_size_respected():
    ctx = make_context(guild_id=None, user_id="999")

    content = "a" * (MAX_MESSAGE_LEN + 10)

    await send_long_response(ctx, content)  # type: ignore

    assert len(ctx.sent_messages) == 2
    assert len(ctx.sent_messages[0]) == MAX_MESSAGE_LEN
