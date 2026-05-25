from typing import Protocol

from semantic_context_server.application.dto.llm_response import LLMResponse


class ResponseCachePort(Protocol):
    async def get(self, key: str) -> LLMResponse | None: ...
    async def set(self, key: str, value: LLMResponse) -> None: ...
