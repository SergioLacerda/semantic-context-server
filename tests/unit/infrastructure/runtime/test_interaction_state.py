import asyncio

from semantic_context_server.infrastructure.runtime.interaction_state import (
    InteractionState,
)

# ==========================================================
# TIME HELPER (SEM MONKEYPATCH 🔥)
# ==========================================================


class FakeTime:
    def __init__(self, values):
        self.values = values

    def __call__(self):
        return self.values.pop(0)


# ==========================================================
# COOLDOWN
# ==========================================================


def test_check_cooldown_allows_first_call():
    runtime = InteractionState(time_provider=lambda: 100)

    assert runtime.check_cooldown("user1", seconds=10) is True


def test_check_cooldown_blocks_within_window():
    time = FakeTime([100, 105])

    runtime = InteractionState(time_provider=time)

    assert runtime.check_cooldown("user1", 10) is True
    assert runtime.check_cooldown("user1", 10) is False


def test_check_cooldown_allows_after_window():
    time = FakeTime([100, 120])

    runtime = InteractionState(time_provider=time)

    assert runtime.check_cooldown("user1", 10) is True
    assert runtime.check_cooldown("user1", 10) is True


# ==========================================================
# WARN (DEBOUNCE)
# ==========================================================


def test_should_warn_first_time():
    runtime = InteractionState(time_provider=lambda: 100)

    assert runtime.should_warn("channel1", debounce=10) is True


def test_should_warn_blocked():
    time = FakeTime([100, 105])

    runtime = InteractionState(time_provider=time)

    assert runtime.should_warn("channel1", 10) is True
    assert runtime.should_warn("channel1", 10) is False


def test_should_warn_after_debounce():
    time = FakeTime([100, 120])

    runtime = InteractionState(time_provider=time)

    assert runtime.should_warn("channel1", 10) is True
    assert runtime.should_warn("channel1", 10) is True


# ==========================================================
# LOCKS
# ==========================================================


def test_get_lock_creates_lock():
    runtime = InteractionState()

    lock = runtime.get_lock("channel1")

    assert isinstance(lock, asyncio.Lock)


def test_get_lock_reuses_same_instance():
    runtime = InteractionState()

    lock1 = runtime.get_lock("channel1")
    lock2 = runtime.get_lock("channel1")

    assert lock1 is lock2


def test_get_lock_different_channels():
    runtime = InteractionState()

    lock1 = runtime.get_lock("channel1")
    lock2 = runtime.get_lock("channel2")

    assert lock1 is not lock2
