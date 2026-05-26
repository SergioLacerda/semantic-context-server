from __future__ import annotations

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class LLMProviderContract(Protocol):
    async def generate(self, request: Any) -> Any: ...


@runtime_checkable
class LLMGatewayContract(Protocol):
    async def generate(self, request: Any) -> Any: ...
