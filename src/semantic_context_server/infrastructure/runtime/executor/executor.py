import asyncio
from typing import Any


class Executor:
    """
    Executor simples e seguro para testes.
    """

    def __init__(self) -> None:
        self._tasks: set[Any] = set()

    async def start(self) -> None:
        pass

    async def run_async(self, fn: Any, *args: Any) -> Any:
        return await self.run(fn, *args)

    async def run(self, fn: Any, *args: Any, **kwargs: Any) -> Any:
        loop = asyncio.get_running_loop()
        task = loop.run_in_executor(None, fn, *args)

        self._tasks.add(task)
        task.add_done_callback(self._tasks.discard)

        return await task

    async def shutdown(self) -> None:
        for t in list(self._tasks):
            t.cancel()
