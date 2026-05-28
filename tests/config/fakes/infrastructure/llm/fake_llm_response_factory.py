from packages.features.llm_gateway.dto import LLMResponse


class FakeLLMResponseFactory:
    @staticmethod
    def create(
        content: str = "ok",
        provider: str = "fake",
        model: str = "fake-model",
        **overrides,
    ) -> LLMResponse:
        return LLMResponse(
            content=content,
            provider=provider,
            model=model,
            latency_ms=overrides.get("latency_ms"),
            tokens_input=overrides.get("tokens_input"),
            tokens_output=overrides.get("tokens_output"),
            raw=overrides.get("raw"),
        )

    @staticmethod
    def from_text(text: str) -> LLMResponse:
        return LLMResponse(
            content=text,
            provider="fake",
            model="test",
        )

    @staticmethod
    def minimal() -> LLMResponse:
        return LLMResponse(
            content="ok",
            provider="fake",
        )
