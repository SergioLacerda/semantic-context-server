from __future__ import annotations

import contextvars
from collections.abc import Generator
from contextlib import contextmanager

_world_id_var: contextvars.ContextVar[str | None] = contextvars.ContextVar("world_id", default=None)
_scope_id_var: contextvars.ContextVar[str | None] = contextvars.ContextVar("scope_id", default=None)


class ScopeContext:
    def set_scope(self, world_id: str, scope_id: str) -> tuple[contextvars.Token, contextvars.Token]:
        return (_world_id_var.set(world_id), _scope_id_var.set(scope_id))

    def get_scope(self) -> tuple[str, str]:
        world_id = _world_id_var.get(None)
        scope_id = _scope_id_var.get(None)
        if world_id is None or scope_id is None:
            raise RuntimeError("No world/scope set in current context")
        return world_id, scope_id

    def reset(self, tokens: tuple[contextvars.Token, contextvars.Token] | None = None) -> None:
        if tokens is not None:
            w, s = tokens
            _world_id_var.reset(w)
            _scope_id_var.reset(s)
            return
        _world_id_var.set(None)
        _scope_id_var.set(None)

    @contextmanager
    def scope(self, world_id: str, scope_id: str) -> Generator[tuple[str, str], None, None]:
        tokens = self.set_scope(world_id, scope_id)
        try:
            yield (world_id, scope_id)
        finally:
            self.reset(tokens)
