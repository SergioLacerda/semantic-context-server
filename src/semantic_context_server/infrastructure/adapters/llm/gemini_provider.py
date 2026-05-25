from typing import Any

try:
    import google.generativeai as genai
except ImportError:
    genai = None

from semantic_context_server.infrastructure.adapters.llm.base_provider import BaseProvider


class GeminiProvider(BaseProvider):
    def __init__(self, api_key: str, model: str, timeout: float = 180.0):
        genai.configure(api_key=api_key)
        super().__init__("gemini", model, timeout=timeout)
        self.model_obj = genai.GenerativeModel(model)

    async def _call_api(self, request: Any) -> Any:
        return await self.model_obj.generate_content_async(
            request.prompt, request_options={"timeout": self.timeout}
        )

    def _extract_content(self, resp: Any) -> str:
        return (getattr(resp, "text", "") or "").strip()
