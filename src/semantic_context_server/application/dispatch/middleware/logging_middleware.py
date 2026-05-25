import logging
import time
from collections.abc import Awaitable, Callable
from typing import Any

logger = logging.getLogger(__name__)


async def logging_middleware(command: Any, ctx: Any, next: Callable[[], Awaitable[Any]]) -> Any:
    start = time.time()

    try:
        return await next()
    finally:
        duration = int((time.time() - start) * 1000)

        logger.info(
            "command=%s user=%s duration=%sms",
            type(command).__name__,
            getattr(ctx.author, "id", "unknown"),
            duration,
        )
