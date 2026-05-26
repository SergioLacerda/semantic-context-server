from typing import Any

import httpx
from openai import AsyncOpenAI

from packages.features.llm_gateway.infrastructure.base_provider import BaseProvider


class GroqProvider(BaseProvider):
    def __init__(self, api_key: str, model: str, timeout: float = 180.0):
        super().__init__("groq", model, timeout=timeout)

        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url="https://api.groq.com/openai/v1",
            timeout=httpx.Timeout(timeout),
        )

    async def _call_api(self, request: Any) -> Any:
        return await self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": request.prompt}],
            temperature=request.temperature,
            max_tokens=request.max_tokens,
        )

    def _extract_content(self, resp: Any) -> str:
        if not resp.choices:
            return ""
        return (resp.choices[0].message.content or "").strip()

    def _extract_usage(self, resp: Any) -> dict[str, Any]:
        return {
            "tokens_input": getattr(resp.usage, "prompt_tokens", None),
            "tokens_output": getattr(resp.usage, "completion_tokens", None),
        }
