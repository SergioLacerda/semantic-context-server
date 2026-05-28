from dataclasses import dataclass

from packages.core.runtime_config.loader import RuntimeSettings


@dataclass(frozen=True)
class HttpApiConfig:
    environment: str
    log_level: int


def from_runtime(settings: RuntimeSettings) -> HttpApiConfig:
    return HttpApiConfig(environment=settings.environment, log_level=settings.log_level)
