import asyncio
import time as _time
from collections.abc import Callable


class InteractionState:
    """Manages per-user cooldowns, per-channel debounce, and per-channel async locks."""

    def __init__(self, time_provider: Callable[[], float] | None = None) -> None:
        self._time = time_provider or _time.time
        self._cooldowns: dict[str, float] = {}
        self._warns: dict[str, float] = {}
        self._locks: dict[str, asyncio.Lock] = {}

    def check_cooldown(self, user_id: str, seconds: float) -> bool:
        now = self._time()
        last = self._cooldowns.get(user_id)
        if last is None or (now - last) >= seconds:
            self._cooldowns[user_id] = now
            return True
        return False

    def should_warn(self, channel_id: str, debounce: float) -> bool:
        now = self._time()
        last = self._warns.get(channel_id)
        if last is None or (now - last) >= debounce:
            self._warns[channel_id] = now
            return True
        return False

    def get_lock(self, channel_id: str) -> asyncio.Lock:
        if channel_id not in self._locks:
            self._locks[channel_id] = asyncio.Lock()
        return self._locks[channel_id]
