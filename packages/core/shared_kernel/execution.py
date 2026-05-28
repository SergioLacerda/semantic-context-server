from __future__ import annotations

import asyncio
import functools
from collections.abc import Callable
from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class ExecutorPort(Protocol):
    async def start(self) -> None: ...
    async def shutdown(self) -> None: ...
    async def run_async(self, fn: Callable[..., Any], *args: Any) -> Any: ...
    async def run(self, fn: Callable[..., Any], *args: Any) -> Any: ...


def on_executor(func: Callable[..., Any]) -> Callable[..., Any]:
    @functools.wraps(func)
    async def wrapper(self: Any, *args: Any, **kwargs: Any) -> Any:
        executor = getattr(self, "executor", None)
        if executor:
            return await executor.run(func, self, *args, **kwargs)
        return await asyncio.to_thread(func, self, *args, **kwargs)

    return wrapper
