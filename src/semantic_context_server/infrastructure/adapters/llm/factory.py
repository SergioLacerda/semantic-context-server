from typing import Any

from semantic_context_server.config.loader import LLMSettings


def create_llm_provider(settings: LLMSettings) -> Any:
    provider = settings.provider.lower()

    # ---------------------------------------------------------
    # OPENAI
    # ---------------------------------------------------------
    if provider == "openai":
        from semantic_context_server.infrastructure.adapters.llm.openai_provider import (
            OpenAIProvider,
        )

        return OpenAIProvider(
            api_key=settings.api_key or "",
            model=settings.model,
            base_url=settings.base_url,
            timeout=settings.timeout,
        )

    # ---------------------------------------------------------
    # LM STUDIO
    # ---------------------------------------------------------
    if provider == "lmstudio":
        from semantic_context_server.infrastructure.adapters.llm.lmstudio_provider import (
            LMStudioProvider,
        )

        return LMStudioProvider(
            model=settings.model,
            base_url=settings.base_url or "http://localhost:1234/v1",
            timeout=settings.timeout,
        )

    # ---------------------------------------------------------
    # OLLAMA
    # ---------------------------------------------------------
    if provider == "ollama":
        from semantic_context_server.infrastructure.adapters.llm.ollama_provider import (
            OllamaProvider,
        )

        return OllamaProvider(
            model=settings.model,
            base_url=settings.base_url or "http://localhost:11434",
            timeout=settings.timeout,
        )

    # ---------------------------------------------------------
    # GROQ
    # ---------------------------------------------------------
    if provider == "groq":
        from semantic_context_server.infrastructure.adapters.llm.groq_provider import GroqProvider

        return GroqProvider(
            api_key=settings.api_key or "",
            model=settings.model,
            timeout=settings.timeout,
        )

    # ---------------------------------------------------------
    # ANTHROPIC
    # ---------------------------------------------------------
    if provider == "anthropic":
        from semantic_context_server.infrastructure.adapters.llm.anthropic_provider import (
            AnthropicProvider,
        )

        return AnthropicProvider(
            api_key=settings.api_key or "",
            model=settings.model,
            timeout=settings.timeout,
        )

    # ---------------------------------------------------------
    # DEEPSEEK
    # ---------------------------------------------------------
    if provider == "deepseek":
        from semantic_context_server.infrastructure.adapters.llm.deepseek_provider import (
            DeepSeekProvider,
        )

        return DeepSeekProvider(
            api_key=settings.api_key or "",
            model=settings.model,
            timeout=settings.timeout,
        )

    # ---------------------------------------------------------
    # GEMINI
    # ---------------------------------------------------------
    if provider == "gemini":
        from semantic_context_server.infrastructure.adapters.llm.gemini_provider import (
            GeminiProvider,
        )

        return GeminiProvider(
            api_key=settings.api_key or "",
            model=settings.model,
            timeout=settings.timeout,
        )

    raise ValueError(
        f"Unknown LLM provider: {provider!r}. "
        "Valid: openai, lmstudio, ollama, groq, anthropic, deepseek, gemini"
    )
