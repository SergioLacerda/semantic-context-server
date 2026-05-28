from __future__ import annotations

import asyncio
import inspect
from collections import defaultdict
from collections.abc import Awaitable, Callable

from packages.core.bootstrap_runtime.events.envelope import EventEnvelope


class InProcessAsyncBus:
    def __init__(self) -> None:
        self._subs: dict[str, list[Callable[[EventEnvelope], Awaitable[None] | None]]] = defaultdict(list)
        self._tasks: set[asyncio.Task[None]] = set()

    async def publish(self, event: EventEnvelope) -> None:
        for handler in list(self._subs.get(event.event_type, [])):
            if inspect.iscoroutinefunction(handler):
                task = asyncio.create_task(handler(event))
            else:
                async def _wrap() -> None:
                    handler(event)
                task = asyncio.create_task(_wrap())
            self._tasks.add(task)
            task.add_done_callback(self._tasks.discard)

    async def subscribe(
        self,
        event_type: str,
        handler: Callable[[EventEnvelope], Awaitable[None] | None],
    ) -> None:
        self._subs[event_type].append(handler)

    async def unsubscribe(
        self,
        event_type: str,
        handler: Callable[[EventEnvelope], Awaitable[None] | None],
    ) -> None:
        self._subs[event_type] = [h for h in self._subs.get(event_type, []) if h is not handler]

    async def flush(self) -> None:
        if self._tasks:
            await asyncio.gather(*list(self._tasks), return_exceptions=True)

    async def shutdown(self) -> None:
        for t in list(self._tasks):
            t.cancel()
        if self._tasks:
            await asyncio.gather(*list(self._tasks), return_exceptions=True)
        self._tasks.clear()
