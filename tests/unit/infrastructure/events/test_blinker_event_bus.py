from semantic_context_server.infrastructure.events.blinker_event_bus import (
    BlinkerEventBus,
)


def test_publish_calls_handler():
    bus = BlinkerEventBus()

    called = {"ok": False}

    def handler(event):
        called["ok"] = True

    class Event:
        pass

    bus.subscribe(Event, handler)

    bus.publish(Event())

    assert called["ok"] is True


def test_multiple_handlers():
    bus = BlinkerEventBus()

    calls = []

    def h1(e):
        calls.append("h1")

    def h2(e):
        calls.append("h2")

    class Event:
        pass

    bus.subscribe(Event, h1)
    bus.subscribe(Event, h2)

    bus.publish(Event())

    assert "h1" in calls
    assert "h2" in calls


def test_event_type_isolated():
    bus = BlinkerEventBus()

    called = {"a": False, "b": False}

    class A:
        pass

    class B:
        pass

    bus.subscribe(A, lambda e: called.update(a=True))
    bus.subscribe(B, lambda e: called.update(b=True))

    bus.publish(A())

    assert called["a"] is True
    assert called["b"] is False
