from typing import Any

import pytest

from semantic_context_server.application.commands.command_bus import CommandBus

# ---------------------------------------------------------
# DUMMIES
# ---------------------------------------------------------


class DummyCommand:
    pass


class DummyHandler:
    def __init__(self, result: Any = "ok"):
        self._result = result

    async def handle(self, command, ctx=None):
        return self._result


class DummyRegistry:
    def __init__(self, mapping):
        self.mapping = mapping

    def get(self, command_type):
        return self.mapping.get(command_type)


class DummyCtx:
    def __init__(self, with_send=True):
        self.sent = []

        if with_send:

            async def send(msg):
                self.sent.append(msg)

            self.send = send


# ---------------------------------------------------------
# TESTS
# ---------------------------------------------------------


@pytest.mark.asyncio
async def test_dispatch_success():
    cmd = DummyCommand()

    bus = CommandBus(
        registry=DummyRegistry({DummyCommand: DummyHandler("ok")}),
    )

    result = await bus.dispatch(DummyCtx(), cmd)

    assert result == "ok"


def test_handler_not_found():
    bus = CommandBus(registry=DummyRegistry({}))

    with pytest.raises(ValueError):
        import asyncio

        asyncio.run(bus.dispatch(None, DummyCommand()))


@pytest.mark.asyncio
async def test_dispatch_without_ctx():
    cmd = DummyCommand()

    bus = CommandBus(
        registry=DummyRegistry({DummyCommand: DummyHandler("ok")}),
    )

    result = await bus.dispatch(None, cmd)

    assert result == "ok"


@pytest.mark.asyncio
async def test_result_none():
    cmd = DummyCommand()

    bus = CommandBus(
        registry=DummyRegistry({DummyCommand: DummyHandler(None)}),
    )

    result = await bus.dispatch(DummyCtx(), cmd)

    assert result is None


# ---------------------------------------------------------
# MIDDLEWARE
# ---------------------------------------------------------


@pytest.mark.asyncio
async def test_middleware_chain():
    cmd = DummyCommand()

    async def middleware(command, ctx, next_call):
        result = await next_call()
        return f"wrapped({result})"

    bus = CommandBus(
        registry=DummyRegistry({DummyCommand: DummyHandler("ok")}),
        middlewares=[middleware],
    )

    result = await bus.dispatch(DummyCtx(), cmd)

    assert result == "wrapped(ok)"
