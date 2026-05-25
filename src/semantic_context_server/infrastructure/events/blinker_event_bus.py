from collections import defaultdict
from collections.abc import Callable
from typing import Any

from blinker import Signal


class BlinkerEventBus:
    def __init__(self) -> None:
        self._signals: defaultdict[type, Signal] = defaultdict(Signal)
        self._receivers: list[Any] = []

    def publish(self, event: object) -> None:
        signal = self._signals[type(event)]
        signal.send(self, event=event)

    def subscribe(self, event_type: type, handler: Callable[[Any], object]) -> None:
        def wrapper(sender: Any, **kwargs: Any) -> None:
            handler(kwargs["event"])

        self._receivers.append(wrapper)
        self._signals[event_type].connect(wrapper, weak=False)

    def _check_for_orphan_receivers(self) -> list[str]:
        """
        Compat helper used by tests/lifecycle guards.
        Returns an empty list when no explicit leak tracking is available.
        """
        return []
