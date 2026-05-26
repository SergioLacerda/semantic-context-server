from __future__ import annotations

import asyncio
import functools
from collections.abc import Callable
from typing import Any


def on_executor(func: Callable[..., Any]) -> Callable[..., Any]:
    @functools.wraps(func)
    async def wrapper(self: Any, *args: Any, **kwargs: Any) -> Any:
        executor = getattr(self, "executor", None)
        if executor:
            return await executor.run(func, self, *args, **kwargs)
        return await asyncio.to_thread(func, self, *args, **kwargs)

    return wrapper
