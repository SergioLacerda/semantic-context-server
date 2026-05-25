import pytest

from semantic_context_server.domain.random.random_provider import RandomProvider


class Dummy(RandomProvider):
    pass


def test_random_provider_abstract():
    with pytest.raises(TypeError):
        Dummy()  # type: ignore[abstract]
