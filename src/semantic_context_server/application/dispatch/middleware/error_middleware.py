import logging
from collections.abc import Awaitable, Callable
from typing import Any

logger = logging.getLogger(__name__)


async def error_middleware(command: Any, ctx: Any, next: Callable[[], Awaitable[Any]]) -> Any:
    try:
        return await next()
    except Exception as e:
        logger.exception("Command failed")

        return f"⚠️ Erro ao executar comando: {str(e)}"
