import pytest

from packages.core.bootstrap_runtime.runtime_scope import ScopeContext


def test_set_and_get():
    ctx = ScopeContext()

    ctx.set_scope("world1", "campaign:abc")

    assert ctx.get_scope() == ("world1", "campaign:abc")


def test_get_without_set():
    ctx = ScopeContext()

    ctx.reset()

    with pytest.raises(RuntimeError):
        ctx.get_scope()


def test_reset_with_tokens():
    ctx = ScopeContext()

    ctx.reset()

    tokens = ctx.set_scope("world1", "campaign:abc")

    ctx.reset(tokens)

    with pytest.raises(RuntimeError):
        ctx.get_scope()


def test_reset_without_tokens():
    ctx = ScopeContext()

    ctx.set_scope("world1", "campaign:abc")
    ctx.reset()

    with pytest.raises(RuntimeError):
        ctx.get_scope()


def test_scope():
    ctx = ScopeContext()

    with ctx.scope("world1", "scope-xyz") as (wid, sid):
        assert wid == "world1"
        assert sid == "scope-xyz"
        assert ctx.get_scope() == ("world1", "scope-xyz")

    with pytest.raises(RuntimeError):
        ctx.get_scope()


def test_context_is_isolated():
    ctx = ScopeContext()

    with ctx.scope("world1", "scope-a"):
        assert ctx.get_scope() == ("world1", "scope-a")

    with ctx.scope("world1", "scope-b"):
        assert ctx.get_scope() == ("world1", "scope-b")
