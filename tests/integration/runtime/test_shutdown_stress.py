import asyncio
import logging

import pytest

from semantic_context_server.infrastructure.runtime.bus.event_bus import EventBus

logger = logging.getLogger(__name__)


def _make_zombie_handler(cancel_count_ref: list, num_zombies: int, cancel_event: asyncio.Event):
    async def handler(bus, event):
        try:
            while True:
                await asyncio.sleep(0.01)
        except asyncio.CancelledError:
            cancel_count_ref[0] += 1
            if cancel_count_ref[0] == num_zombies:
                cancel_event.set()
            raise

    return handler


def _subscribe_zombies(
    event_bus, event_cls, num_zombies: int, cancel_count_ref: list, cancel_event: asyncio.Event
) -> None:
    for _ in range(num_zombies):
        handler = _make_zombie_handler(cancel_count_ref, num_zombies, cancel_event)
        event_bus.subscribe(event_cls, handler)


@pytest.mark.asyncio
async def test_container_shutdown_interrupts_mass_infinite_handlers(container):
    """
    WORLD CLASS STRESS TEST:
    Valida se o shutdown do container interrompe centenas de handlers infinitos
    sem deixar leaks ou travar o processo.
    """
    event_bus = container.resolve(EventBus)
    num_zombies = 50
    cancel_event = asyncio.Event()
    cancel_count_ref = [0]

    class StressEvent:
        pass

    _subscribe_zombies(event_bus, StressEvent, num_zombies, cancel_count_ref, cancel_event)

    await event_bus.publish(StressEvent())
    await asyncio.sleep(0.1)

    await asyncio.wait_for(container.shutdown(), timeout=2.0)

    assert cancel_count_ref[0] == num_zombies, (
        f"Esperado {num_zombies} cancelamentos, obtido {cancel_count_ref[0]}"
    )
    assert cancel_event.is_set(), "O evento de conclusão de cancelamento não foi disparado"
