from unittest.mock import AsyncMock

import pytest

from semantic_context_server.application.contracts.response import Response
from tests.config.harness.message_harness import MessageHarness
from tests.config.helpers.asserts import assert_response, assert_text


def make_msg(content="attack"):
    return type("Msg", (), {"content": content, "author": type("A", (), {"bot": False})})()


@pytest.mark.asyncio
async def test_send_response_chunking():
    h = MessageHarness()

    service = h.build()

    long_text = "a" * 4000

    await service._send_response(h.ctx, long_text)

    assert len(h.sent) == 3


@pytest.mark.asyncio
async def test_send_response_short():
    h = MessageHarness()

    service = h.build()

    await service._send_response(h.ctx, "ok")

    assert h.sent == ["ok"]


@pytest.mark.asyncio
async def test_execute_and_send_success():
    h = MessageHarness(response="hello")

    service = h.build()

    await service._execute_and_send(
        h.ctx,
        await h.deps.resolve_campaign("camp"),
        "camp",
        "attack",
        "user",
        intent="ACTION",
    )

    assert h.sent == ["hello"]


@pytest.mark.asyncio
async def test_execute_and_send_empty_response():
    h = MessageHarness(response=None)

    service = h.build()

    await service._execute_and_send(
        h.ctx,
        await h.deps.resolve_campaign("camp"),
        "camp",
        "attack",
        "user",
        intent="ACTION",
    )

    assert h.sent == []


@pytest.mark.asyncio
async def test_handle_success_flow():
    h = MessageHarness(response="ok", campaign_id="camp1")

    msg = make_msg()

    service = h.build()

    await service.handle(msg, h.ctx, h.ctx)

    assert h.sent == ["ok"]


@pytest.mark.asyncio
async def test_handle_respects_cooldown():
    h = MessageHarness(cooldown=False)

    msg = make_msg()

    service = h.build()

    await service.handle(msg, h.ctx, h.ctx)

    assert h.sent == []


@pytest.mark.asyncio
async def test_handle_ignores_ooc_messages():
    h = MessageHarness(intent="OOC")

    msg = make_msg()

    service = h.build()

    await service.handle(msg, h.ctx, h.ctx)

    assert h.sent == []


@pytest.mark.asyncio
async def test_handle_respects_lock():
    h = MessageHarness(locked=True)

    msg = make_msg()

    service = h.build()

    await service.handle(msg, h.ctx, h.ctx)

    assert h.sent == []


@pytest.mark.asyncio
async def test_handle_ignores_bot():
    h = MessageHarness()

    msg = type("Msg", (), {"content": "attack", "author": type("A", (), {"bot": True})})()

    service = h.build()

    await service.handle(msg, h.ctx, h.ctx)

    assert h.sent == []


@pytest.mark.asyncio
async def test_handle_ignores_empty():
    h = MessageHarness()

    msg = make_msg(content="   ")

    service = h.build()

    await service.handle(msg, h.ctx, h.ctx)

    assert h.sent == []


@pytest.mark.asyncio
async def test_handle_intent_exception_fallback():
    h = MessageHarness(campaign_id="test")
    h.intent.classify = AsyncMock(side_effect=Exception())

    msg = make_msg()
    service = h.build()

    await service.handle(msg, h.ctx, h.ctx)

    assert h.sent != []


@pytest.mark.asyncio
async def test_execute_and_send_raises_on_failure():
    h = MessageHarness()

    h.usecases.narrative.execute = AsyncMock(side_effect=ValueError())

    service = h.build()

    with pytest.raises(ValueError):
        await service._execute_and_send(
            h.ctx,
            await h.deps.resolve_campaign("camp"),
            "camp",
            "attack",
            "user",
            intent="ACTION",
        )


def test_adapt_response_unknown_intent():
    h = MessageHarness()

    service = h.build()

    result = service._adapt_response_by_intent("hello", "UNKNOWN")

    assert_text(result, "hello")


def test_adapt_response_empty():
    h = MessageHarness()

    service = h.build()

    result = service._adapt_response_by_intent("", "ACTION")

    assert_response(result)
    assert result.text == ""


def test_adapt_response_chat():
    h = MessageHarness()
    service = h.build()

    result = service._adapt_response_by_intent("x", "CHAT")
    assert_text(result, "x")
    assert result.type == "chat"


def test_adapt_response_exploration():
    h = MessageHarness()
    service = h.build()

    result = service._adapt_response_by_intent("x", "EXPLORATION")

    assert isinstance(result, Response)
    assert_text(result, "x")
    assert result.type == "exploration"


def test_adapt_response_action():
    h = MessageHarness()
    service = h.build()

    result = service._adapt_response_by_intent("x", "ACTION")

    assert_text(result, "x")
    assert result.type == "action"
