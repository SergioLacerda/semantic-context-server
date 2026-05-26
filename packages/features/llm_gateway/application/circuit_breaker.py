import time


class CircuitBreaker:
    """
    Simple Circuit Breaker for protecting LLM calls.

    States:
        CLOSED     → normal operation
        OPEN       → blocking calls
        HALF_OPEN  → testing recovery (single trial)
    """

    def __init__(
        self,
        failure_threshold: int = 3,
        recovery_time: float = 10.0,
    ):
        self.failure_threshold = failure_threshold
        self.recovery_time = recovery_time

        self.failures = 0
        self.last_failure: float | None = None
        self.state = "CLOSED"

        # controla tentativa única no HALF_OPEN
        self._half_open_trial = False

    # ---------------------------------------------------------
    # PUBLIC
    # ---------------------------------------------------------

    def allow(self) -> bool:
        now = time.time()

        # -----------------------------
        # OPEN → verificar recuperação
        # -----------------------------
        if self.state == "OPEN":
            if self.last_failure is None:
                return False

            if now - self.last_failure >= self.recovery_time:
                self.state = "HALF_OPEN"
                self._half_open_trial = False
            else:
                return False

        # -----------------------------
        # HALF_OPEN → permitir apenas 1 tentativa
        # -----------------------------
        if self.state == "HALF_OPEN":
            if self._half_open_trial:
                return False

            self._half_open_trial = True
            return True

        # -----------------------------
        # CLOSED → sempre permite
        # -----------------------------
        return True

    # ---------------------------------------------------------

    def success(self) -> None:
        """
        Called when a request succeeds.
        Resets breaker to CLOSED.
        """
        self.failures = 0
        self.state = "CLOSED"
        self._half_open_trial = False

    # ---------------------------------------------------------

    def failure(self) -> None:
        """
        Called when a request fails.
        Updates failure count and possibly opens the circuit.
        """
        now = time.time()

        # HALF_OPEN → falhou → volta direto pra OPEN
        if self.state == "HALF_OPEN":
            self.state = "OPEN"
            self.failures = self.failure_threshold
            self.last_failure = now
            self._half_open_trial = False
            return

        # CLOSED → acumula falhas
        self.failures += 1
        self.last_failure = now

        if self.failures >= self.failure_threshold:
            self.state = "OPEN"
