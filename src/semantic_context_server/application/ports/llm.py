from typing import Protocol, runtime_checkable

from semantic_context_server.application.dto.llm_request import LLMRequest
from semantic_context_server.application.dto.llm_response import LLMResponse


@runtime_checkable
class LLMServicePort(Protocol):
    async def generate(self, request: LLMRequest) -> LLMResponse: ...
