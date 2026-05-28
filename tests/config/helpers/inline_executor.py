import inspect
from collections.abc import Callable
from typing import Any


class InlineExecutor:
    async def start(self) -> None:
        return None

    async def shutdown(self) -> None:
        return None

    async def run_async(self, fn: Callable[..., Any], *args: Any) -> Any:
        return await self.run(fn, *args)

    async def run(self, fn: Callable[..., Any], *args: Any) -> Any:
        if inspect.iscoroutinefunction(fn):
            return await fn(*args)
        return fn(*args)
