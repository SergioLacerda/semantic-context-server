from __future__ import annotations

from collections import defaultdict
from collections.abc import Awaitable, Callable
from typing import Any

from blinker import Signal

from packages.core.bootstrap_runtime.events.envelope import EventEnvelope


class InProcessSyncBus:
    def __init__(self) -> None:
        self._signals: defaultdict[type, Signal] = defaultdict(Signal)
        self._wrappers: dict[tuple[str, int], Callable[..., object]] = {}

    async def publish(self, event: EventEnvelope) -> None:
        signal = self._signals[type(event)]
        signal.send(self, event=event)

    async def subscribe(
        self,
        event_type: str,
        handler: Callable[[EventEnvelope], Awaitable[None] | None],
    ) -> None:
        def _wrapper(evt: EventEnvelope) -> None:
            if evt.event_type != event_type:
                return
            result = handler(evt)
            if result is not None:
                # sync bus intentionally ignores coroutine results for compatibility
                return None

        key = (event_type, id(handler))
        self._wrappers[key] = _wrapper
        def _signal_wrapper(sender: Any, **kwargs: Any) -> None:
            _wrapper(kwargs["event"])

        self._signals[EventEnvelope].connect(_signal_wrapper, weak=False)

    async def unsubscribe(
        self,
        event_type: str,
        handler: Callable[[EventEnvelope], Awaitable[None] | None],
    ) -> None:
        self._wrappers.pop((event_type, id(handler)), None)

    async def flush(self) -> None:
        return None

    async def shutdown(self) -> None:
        return None
