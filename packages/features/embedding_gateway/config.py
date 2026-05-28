from dataclasses import dataclass

from packages.core.runtime_config.loader import EmbeddingSettings


@dataclass(frozen=True)
class EmbeddingGatewayConfig:
    provider: str
    model: str
    api_key: str | None
    base_url: str | None
    batch_size: int
    dimension: int
    timeout: int


def from_runtime(settings: EmbeddingSettings) -> EmbeddingGatewayConfig:
    return EmbeddingGatewayConfig(
        provider=settings.provider,
        model=settings.model,
        api_key=settings.api_key,
        base_url=settings.base_url,
        batch_size=settings.batch_size,
        dimension=settings.dimension,
        timeout=settings.timeout,
    )
