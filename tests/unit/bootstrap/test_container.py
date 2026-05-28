import pytest

from packages.core.bootstrap_runtime.runtime_scope import InteractionState
from semantic_context_server.application.ports.interaction_runtime import InteractionRuntimePort
from semantic_context_server.bootstrap.container import Container
from semantic_context_server.bootstrap.modules.runtime_module import RuntimeModule


class DummyPort:
    pass


def test_register_duplicate_same_instance_is_allowed():
    container = Container()
    instance = DummyPort()

    container.register(DummyPort, instance)
    container.register(DummyPort, instance)

    assert container.resolve(DummyPort) is instance


def test_register_duplicate_different_instance_raises():
    container = Container()
    instance_one = DummyPort()
    instance_two = DummyPort()

    container.register(DummyPort, instance_one)

    with pytest.raises(ValueError, match="Dependency port already registered"):
        container.register(DummyPort, instance_two)


def test_interaction_state_property_resolves_runtime_port():
    container = Container()
    RuntimeModule().configure(container)

    assert container.interaction_state is container.resolve(InteractionRuntimePort)
    assert isinstance(container.interaction_state, InteractionState)
    assert not hasattr(container, "_interaction_state")
