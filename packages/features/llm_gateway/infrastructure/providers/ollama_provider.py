from typing import Any

import httpx

from packages.features.llm_gateway.infrastructure.base_provider import BaseProvider


class OllamaProvider(BaseProvider):
    def __init__(self, model: str, base_url: str, timeout: float = 180.0):
        super().__init__("ollama", model, timeout=timeout)
        self.client = httpx.AsyncClient(base_url=base_url, timeout=timeout)

    async def _call_api(self, request: Any) -> Any:
        return await self.client.post(
            "/api/generate",
            json={
                "model": self.model,
                "prompt": request.prompt,
                "stream": False,
            },
        )

    def _extract_content(self, resp: Any) -> str:
        data = resp.json()
        return (data.get("response") or "").strip()
