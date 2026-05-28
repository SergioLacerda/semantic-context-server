from dataclasses import dataclass, field, replace
from typing import Any, Optional


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

    def __post_init__(self) -> None:
        if not self.prompt or not self.prompt.strip():
            raise ValueError("LLMRequest.prompt cannot be empty")
        if not self.campaign_id:
            raise ValueError("LLMRequest.campaign_id is required")
        if not (0 <= self.temperature <= 2):
            raise ValueError("temperature must be between 0 and 2")
        if self.max_tokens <= 0:
            raise ValueError("max_tokens must be > 0")
        object.__setattr__(self, "prompt", self.prompt.strip())

    def copy_with(self, **kwargs: Any) -> "LLMRequest":
        return replace(self, **kwargs)


@dataclass
class LLMResponse:
    content: str
    provider: str
    model: str | None = None
    latency_ms: float | None = None
    tokens_input: int | None = None
    tokens_output: int | None = None
    raw: dict[str, Any] | None = None

    def to_dict(self) -> dict:
        return {
            "v": 1,
            "content": self.content,
            "provider": self.provider,
            "model": self.model,
            "latency_ms": self.latency_ms,
            "tokens_input": self.tokens_input,
            "tokens_output": self.tokens_output,
            "raw": self.raw,
        }

    @classmethod
    def from_dict(cls, data: dict) -> Optional["LLMResponse"]:
        if not data:
            return None
        if isinstance(data, str):
            return cls(content=data, provider="unknown")

        version = data.get("v", 1)
        if version == 1:
            return cls(
                content=data.get("content", ""),
                provider=data.get("provider", "unknown"),
                model=data.get("model"),
                latency_ms=data.get("latency_ms"),
                tokens_input=data.get("tokens_input"),
                tokens_output=data.get("tokens_output"),
                raw=data.get("raw"),
            )

        return cls(content=str(data), provider="unknown")
