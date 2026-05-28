from dataclasses import dataclass

from packages.core.runtime_config.loader import LLMSettings


@dataclass(frozen=True)
class LLMGatewayConfig:
    provider: str
    model: str
    api_key: str | None
    base_url: str | None
    timeout: int


def from_runtime(settings: LLMSettings) -> LLMGatewayConfig:
    return LLMGatewayConfig(
        provider=settings.provider,
        model=settings.model,
        api_key=settings.api_key,
        base_url=settings.base_url,
        timeout=settings.timeout,
    )
