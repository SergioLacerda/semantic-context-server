from dataclasses import dataclass, field, replace
from typing import Any


@dataclass(frozen=True, slots=True)
class LLMRequest:
    prompt: str
    campaign_id: str

    system_prompt: str | None = None
    temperature: float = 0.7
    max_tokens: int = 1000
    timeout: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    intent: str | None = None

    # ======================================================
    # VALIDATION
    # ======================================================

    def __post_init__(self) -> None:
        if not self.prompt or not self.prompt.strip():
            raise ValueError("LLMRequest.prompt cannot be empty")

        if not self.campaign_id:
            raise ValueError("LLMRequest.campaign_id is required")

        if not (0 <= self.temperature <= 2):
            raise ValueError("temperature must be between 0 and 2")

        if self.max_tokens <= 0:
            raise ValueError("max_tokens must be > 0")

        # garantir normalização sem quebrar imutabilidade
        object.__setattr__(self, "prompt", self.prompt.strip())

    # ======================================================
    # IMMUTABLE COPY
    # ======================================================

    def copy_with(self, **kwargs: Any) -> "LLMRequest":
        return replace(self, **kwargs)
