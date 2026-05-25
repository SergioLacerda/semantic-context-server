from semantic_context_server.infrastructure.random.default_random import (
    DefaultRandomProvider,
)
from semantic_context_server.infrastructure.random.python_random_provider import (
    PythonRandomProvider,
)


def test_roll_range():
    rng = PythonRandomProvider()

    for _ in range(20):
        value = rng.roll(6)
        assert 1 <= value <= 6


def test_default_random():
    rng = DefaultRandomProvider()

    for _ in range(20):
        value = rng.roll(10)
        assert 1 <= value <= 10
