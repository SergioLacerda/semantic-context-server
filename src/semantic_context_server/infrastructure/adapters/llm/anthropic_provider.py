from typing import Any

try:
    import anthropic
except ImportError:
    anthropic = None

from semantic_context_server.infrastructure.adapters.llm.base_provider import BaseProvider


class AnthropicProvider(BaseProvider):
    def __init__(self, api_key: str, model: str, timeout: float = 180.0):
        super().__init__("anthropic", model, timeout=timeout)
        self.client = anthropic.AsyncAnthropic(api_key=api_key, timeout=timeout)

    async def _call_api(self, request: Any) -> Any:
        return await self.client.messages.create(
            model=self.model,
            max_tokens=request.max_tokens,
            messages=[{"role": "user", "content": request.prompt}],
        )

    def _extract_content(self, resp: Any) -> str:
        parts = []
        for block in getattr(resp, "content", []):
            if getattr(block, "text", None):
                parts.append(block.text)
        return "".join(parts).strip()
