import pytest

from semantic_context_server.application.commands.command_registry import (
    CommandRegistry,
)
from semantic_context_server.application.commands.gm.command import GMCommand

# ---------------------------------------------------------
# DUMMIES
# ---------------------------------------------------------


class DummyCommand:
    pass


class DummyHandler:
    pass


# ---------------------------------------------------------
# TESTS
# ---------------------------------------------------------


def test_register_and_get_handler():
    registry = CommandRegistry()
    handler = DummyHandler()

    registry.register(DummyCommand, handler, name="dummy")

    assert registry.get(DummyCommand) is handler


def test_get_command_type_by_name():
    registry = CommandRegistry()

    registry.register(DummyCommand, DummyHandler(), name="dummy", aliases=["d"])

    assert registry.get_command("dummy") is DummyCommand
    assert registry.get_command("D") is DummyCommand  # Case insensitive


def test_get_not_found():
    registry = CommandRegistry()

    assert registry.get(DummyCommand) is None
    assert registry.get_command("missing") is None


def test_list_commands():
    registry = CommandRegistry()

    registry.register(DummyCommand, DummyHandler(), name="cmd1")
    registry.register(GMCommand, DummyHandler(), name="gm")

    commands = registry.list_commands()

    assert "cmd1" in commands
    assert "gm" in commands


def test_duplicate_registration_raises_error():
    registry = CommandRegistry()
    registry.register(DummyCommand, DummyHandler(), name="cmd")

    with pytest.raises(RuntimeError, match="Handler already registered"):
        registry.register(DummyCommand, DummyHandler())

    with pytest.raises(RuntimeError, match="Command name already registered"):
        registry.register(GMCommand, DummyHandler(), name="cmd")


def test_metadata_enrichment():
    registry = CommandRegistry()

    registry.register(DummyCommand, DummyHandler(), name="test", meta={"category": "System"})

    meta = registry.get_meta(DummyCommand)
    assert meta["name"] == "test"
    assert meta["category"] == "System"
    assert "description" in meta
