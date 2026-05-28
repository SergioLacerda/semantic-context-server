from __future__ import annotations

from typing import Protocol, runtime_checkable

from packages.features.llm_gateway.dto import LLMRequest, LLMResponse


@runtime_checkable
class LLMProviderContract(Protocol):
    async def generate(self, request: LLMRequest) -> LLMResponse: ...


@runtime_checkable
class LLMGatewayContract(Protocol):
    async def generate(self, request: LLMRequest) -> LLMResponse: ...
