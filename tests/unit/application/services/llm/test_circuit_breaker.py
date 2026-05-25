import time

from semantic_context_server.application.services.llm.circuit_breaker import CircuitBreaker


def test_initial_state():
    cb = CircuitBreaker()

    assert cb.state == "CLOSED"
    assert cb.allow() is True


def test_open_after_threshold():
    cb = CircuitBreaker(failure_threshold=2)

    cb.failure()
    assert cb.state == "CLOSED"

    cb.failure()
    assert cb.state == "OPEN"


def test_open_blocks_calls():
    cb = CircuitBreaker(failure_threshold=1)

    cb.failure()

    assert cb.state == "OPEN"
    assert cb.allow() is False


def test_half_open_single_trial():
    cb = CircuitBreaker(failure_threshold=1, recovery_time=0.1)

    cb.failure()
    time.sleep(0.2)

    assert cb.allow() is True  # primeira tentativa
    assert cb.allow() is False  # bloqueia segunda


def test_half_open_success_resets():
    cb = CircuitBreaker(failure_threshold=1, recovery_time=0.1)

    cb.failure()
    time.sleep(0.2)

    cb.allow()  # entra em HALF_OPEN
    cb.success()

    assert cb.state == "CLOSED"
    assert cb.failures == 0


def test_half_open_failure_reopens():
    cb = CircuitBreaker(failure_threshold=3, recovery_time=0.1)

    cb.failure()
    cb.failure()
    cb.failure()

    time.sleep(0.2)

    cb.allow()  # HALF_OPEN
    cb.failure()

    assert cb.state == "OPEN"


def test_success_resets_everything():
    cb = CircuitBreaker(failure_threshold=1)

    cb.failure()
    assert cb.state == "OPEN"

    cb.success()

    assert cb.state == "CLOSED"
    assert cb.failures == 0


def test_failure_increments():
    cb = CircuitBreaker()

    cb.failure()
    cb.failure()

    assert cb.failures == 2


def test_last_failure_set():
    cb = CircuitBreaker()

    cb.failure()

    assert cb.last_failure is not None


def test_zero_recovery_time():
    cb = CircuitBreaker(failure_threshold=1, recovery_time=0)

    cb.failure()

    assert cb.allow() is True
    assert cb.state == "HALF_OPEN"
