from __future__ import annotations

from typing import Any

from packages.features.llm_gateway.contracts import LLMGatewayContract, LLMProviderContract


class LLMGatewayService(LLMGatewayContract):
    """Centralized LLM provider integration consumed via contracts."""

    def __init__(self, providers: dict[str, LLMProviderContract], default_provider: str) -> None:
        if default_provider not in providers:
            raise ValueError(f"Unknown default provider: {default_provider}")
        self._providers = providers
        self._default_provider = default_provider

    async def generate(self, request: Any) -> Any:
        return await self._providers[self._default_provider].generate(request)
