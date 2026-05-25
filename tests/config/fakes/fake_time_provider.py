class FakeTimeProvider:
    """
    Provedor de tempo determinístico para testes.
    Substitui time.time() permitindo avançar o tempo manualmente.
    """

    def __init__(self, initial_time: float = 1600000000.0):
        self._now = initial_time

    def __call__(self) -> float:
        """Simula a chamada time.time()"""
        return self._now

    def _advance(self, seconds: float):
        """Avança o relógio artificialmente."""
        self._now += seconds

    def _set_time(self, timestamp: float):
        self._now = timestamp
