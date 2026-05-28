from __future__ import annotations

import asyncio
import time as _time
from collections.abc import Callable


class InteractionState:
    """Cooldown/debounce/lock primitives for runtime scopes."""

    def __init__(self, time_provider: Callable[[], float] | None = None) -> None:
        self._time = time_provider or _time.time
        self._cooldowns: dict[str, float] = {}
        self._warns: dict[str, float] = {}
        self._locks: dict[str, asyncio.Lock] = {}

    def check_cooldown(self, actor_id: str, seconds: float) -> bool:
        now = self._time()
        last = self._cooldowns.get(actor_id)
        if last is None or (now - last) >= seconds:
            self._cooldowns[actor_id] = now
            return True
        return False

    def should_warn(self, channel_id: str, debounce: float) -> bool:
        now = self._time()
        last = self._warns.get(channel_id)
        if last is None or (now - last) >= debounce:
            self._warns[channel_id] = now
            return True
        return False

    def get_lock(self, key: str) -> asyncio.Lock:
        if key not in self._locks:
            self._locks[key] = asyncio.Lock()
        return self._locks[key]
