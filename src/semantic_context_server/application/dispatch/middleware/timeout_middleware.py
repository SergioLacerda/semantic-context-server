import asyncio
from collections.abc import Awaitable, Callable
from typing import Any


async def timeout_middleware(command: Any, ctx: Any, next: Callable[[], Awaitable[Any]]) -> Any:
    timeout = getattr(ctx, "timeout", 180)

    try:
        return await asyncio.wait_for(next(), timeout=timeout)
    except TimeoutError:
        return "⏱️ Tempo limite excedido."
