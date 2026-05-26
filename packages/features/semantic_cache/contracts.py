from __future__ import annotations

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class SemanticCacheContract(Protocol):
    async def get(self, prompt: str) -> Any | None: ...

    async def set(self, prompt: str, value: Any) -> None: ...

    async def invalidate(self, prompt: str) -> None: ...

    async def clear(self) -> None: ...
