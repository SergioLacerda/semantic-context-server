from typing import Any

from semantic_context_server.application.ports.embedding_gateway import EmbeddingGateway
from semantic_context_server.config.loader import EmbeddingSettings
from semantic_context_server.infrastructure.embeddings.service.embedding_service import (
    EmbeddingService,
)

from .registry import EmbeddingRegistry

# ---------------------------------------------------------
# GLOBAL REGISTRY (singleton leve)
# ---------------------------------------------------------
_registry = EmbeddingRegistry()


def _register_default_providers() -> None:
    # evitar re-registro
    if _registry.list_providers():
        return

    # ---------------------------------------------------------
    # sentence-transformers
    # ---------------------------------------------------------
    from semantic_context_server.infrastructure.embeddings.providers.sentence_embedding_provider import (
        SentenceEmbeddingProvider,
    )

    _registry.register(
        "sentence",
        lambda **kwargs: SentenceEmbeddingProvider(
            model=kwargs.get("model") or "all-MiniLM-L6-v2",
            device=kwargs.get("device"),
        ),
    )

    # ---------------------------------------------------------
    # OpenAI
    # ---------------------------------------------------------
    from semantic_context_server.infrastructure.embeddings.providers.openai_embedding_provider import (
        OpenAIEmbeddingProvider,
    )

    _registry.register(
        "openai",
        lambda **kwargs: OpenAIEmbeddingProvider(
            api_key=kwargs.get("api_key") or "",
            model=kwargs.get("model") or "text-embedding-3-small",
            base_url=kwargs.get("base_url"),
            timeout=kwargs.get("timeout", 180.0),
        ),
    )

    # ---------------------------------------------------------
    # Ollama
    # ---------------------------------------------------------
    from semantic_context_server.infrastructure.embeddings.providers.ollama_embedding_provider import (
        OllamaEmbeddingProvider,
    )

    _registry.register(
        "ollama",
        lambda **kwargs: OllamaEmbeddingProvider(
            model=kwargs.get("model") or "",
            base_url=kwargs.get("base_url") or "http://localhost:11434",
            timeout=kwargs.get("timeout", 180.0),
        ),
    )

    # ---------------------------------------------------------
    # LM Studio
    # ---------------------------------------------------------
    from semantic_context_server.infrastructure.embeddings.providers.lmstudio_embedding_provider import (
        LMStudioEmbeddingProvider,
    )

    _registry.register(
        "lmstudio",
        lambda **kwargs: LMStudioEmbeddingProvider(
            model=kwargs.get("model") or "",
            base_url=kwargs.get("base_url") or "http://localhost:1234/v1",
            timeout=kwargs.get("timeout", 180.0),
        ),
    )

    # ---------------------------------------------------------
    # Gemini
    # ---------------------------------------------------------
    from semantic_context_server.infrastructure.embeddings.providers.gemini_embedding_provider import (
        GeminiEmbeddingProvider,
    )

    _registry.register(
        "gemini",
        lambda **kwargs: GeminiEmbeddingProvider(
            api_key=kwargs.get("api_key") or "",
            model=kwargs.get("model") or "models/embedding-001",
            timeout=kwargs.get("timeout", 180.0),
        ),
    )


# ---------------------------------------------------------
# PUBLIC FACTORY
# ---------------------------------------------------------
def create_embedding(
    settings: EmbeddingSettings,
    executor: Any = None,
    cache: Any = None,
    device: str | None = None,
) -> EmbeddingGateway:
    _register_default_providers()

    provider_name = settings.provider.lower()

    # 1. Cria o provedor primário configurado
    primary_provider = _registry.create(
        provider_name,
        model=settings.model,
        device=device,
        api_key=settings.api_key,
        base_url=settings.base_url,
        timeout=settings.timeout,
    )

    # 2. Retorna o Service que orquestra o lifecycle e resiliência
    return EmbeddingService(
        providers=[primary_provider],
        target_dim=settings.dimension,
        executor=executor,
        timeout=settings.timeout,
        cache=cache,
    )
