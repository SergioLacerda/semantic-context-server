from typing import Any

import httpx
from openai import AsyncOpenAI

from semantic_context_server.infrastructure.adapters.llm.base_provider import BaseProvider


class LMStudioProvider(BaseProvider):
    """
    Provider compatível com LM Studio (API OpenAI-like).

    Responsabilidade:
    - chamar API
    - extrair conteúdo bruto (str)

    NÃO:
    - cache
    - retry
    - circuit breaker
    (isso é responsabilidade do LLMService)
    """

    def __init__(self, base_url: str, model: str, timeout: float = 180.0):
        if not base_url.endswith("/v1"):
            base_url = base_url.rstrip("/") + "/v1"

        super().__init__("lmstudio", model, timeout=timeout)

        self.client = AsyncOpenAI(
            base_url=base_url,
            api_key="lm-studio",
            timeout=httpx.Timeout(timeout),
        )

    async def _call_api(self, request: Any) -> Any:
        messages: Any = self._build_messages(request)

        try:
            return await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=request.temperature,
                max_tokens=min(request.max_tokens or 400, 400),
            )

        except TimeoutError as e:
            raise TimeoutError("LM Studio timeout.") from e

        except ValueError as e:
            raise ValueError("LM Studio error.") from e

        except Exception as e:
            raise RuntimeError(f"LM Studio unexpected error: {str(e)}") from e

    def _extract_content(self, resp: Any) -> str:
        if not resp or not getattr(resp, "choices", None):
            return ""

        choice = resp.choices[0]

        msg = getattr(choice, "message", None)
        if msg:
            content = getattr(msg, "content", None)
            if content:
                return str(content).strip()

        delta = getattr(choice, "delta", None)
        if delta:
            content = getattr(delta, "content", None)
            if content:
                return str(content).strip()

        text = getattr(choice, "text", None)
        if text:
            return str(text).strip()

        return ""

    async def stream(self, request: Any) -> Any:
        messages: Any = self._build_messages(request)

        stream: Any = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=request.temperature,
            max_tokens=min(request.max_tokens or 400, 400),
            stream=True,
        )

        async for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta

    def _build_messages(self, request: Any) -> list[dict[str, Any]]:
        messages = []

        if getattr(request, "system_prompt", None):
            messages.append({"role": "system", "content": request.system_prompt})

        messages.append({"role": "user", "content": request.prompt})

        return messages
