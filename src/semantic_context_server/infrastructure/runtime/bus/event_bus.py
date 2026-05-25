import asyncio
import inspect
from typing import Any


class EventBus:
    def __init__(self) -> None:
        self._handlers: dict[type, list[Any]] = {}
        self._tasks: set[asyncio.Task[Any]] = set()

    def subscribe(self, event_cls: Any, handler: Any) -> None:
        self._handlers.setdefault(event_cls, []).append(handler)

    async def publish(self, event: Any) -> None:
        handlers = self._handlers.get(type(event), [])
        for handler in handlers:
            if inspect.iscoroutinefunction(handler):
                task: asyncio.Task[Any] = asyncio.create_task(handler(self, event))
                self._tasks.add(task)
                task.add_done_callback(self._tasks.discard)
            else:
                handler(self, event)

    async def shutdown(self) -> None:
        tasks = list(self._tasks)
        for task in tasks:
            task.cancel()
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
        self._tasks.clear()
