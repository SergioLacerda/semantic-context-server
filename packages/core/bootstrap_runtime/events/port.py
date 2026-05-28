from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any, Protocol, runtime_checkable

from packages.core.bootstrap_runtime.events.envelope import EventEnvelope


@runtime_checkable
class EventBusPort(Protocol):
    async def publish(self, event: EventEnvelope) -> None: ...
    async def subscribe(
        self,
        event_type: str,
        handler: Callable[[EventEnvelope], Awaitable[None] | None],
    ) -> None: ...
    async def unsubscribe(
        self,
        event_type: str,
        handler: Callable[[EventEnvelope], Awaitable[None] | None],
    ) -> None: ...
    async def flush(self) -> None: ...
    async def shutdown(self) -> None: ...
