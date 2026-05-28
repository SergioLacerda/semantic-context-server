from __future__ import annotations

from types import SimpleNamespace

import pytest

import packages.interfaces.http_api.assembler as assembler_mod
from packages.interfaces.http_api.app import orchestrated_lifespan


class _FakeApp:
    def __init__(self) -> None:
        self.state = SimpleNamespace()


@pytest.mark.asyncio
async def test_bootstrap_runtime_starts_and_populates_state() -> None:
    app = _FakeApp()
    async with orchestrated_lifespan(app):
        assert getattr(app.state, "service_graph", None) is not None
        assert getattr(app.state, "runtime", None) is not None
        assert getattr(app.state, "container", None) is not None
        assert getattr(app.state, "cache_manager", None) is not None
        assert app.state.orchestrator.ready() is True


@pytest.mark.asyncio
async def test_bootstrap_runtime_shutdown_flips_ready_false() -> None:
    app = _FakeApp()
    orchestrator = None

    async with orchestrated_lifespan(app):
        orchestrator = app.state.orchestrator
        assert orchestrator.ready() is True

    assert orchestrator is not None
    assert orchestrator.ready() is False


@pytest.mark.asyncio
async def test_bootstrap_runtime_preflight_failure_bubbles(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def _invalid_settings() -> None:
        raise RuntimeError("invalid_settings")

    monkeypatch.setattr(assembler_mod, "load_settings", _invalid_settings)

    app = _FakeApp()
    with pytest.raises(RuntimeError, match="config"):
        async with orchestrated_lifespan(app):
            pass
