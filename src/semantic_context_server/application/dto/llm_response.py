from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class LLMResponse:
    content: str

    provider: str
    model: str | None = None

    # métricas
    latency_ms: float | None = None
    tokens_input: int | None = None
    tokens_output: int | None = None

    raw: dict[str, Any] | None = None

    # ---------------------------------------------------------
    # SERIALIZAÇÃO
    # ---------------------------------------------------------

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

    # ---------------------------------------------------------
    # DESERIALIZAÇÃO
    # ---------------------------------------------------------

    @classmethod
    def from_dict(cls, data: dict) -> Optional["LLMResponse"]:
        if not data:
            return None

        if isinstance(data, str):
            return cls(
                content=data,
                provider="unknown",
            )

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

        # fallback
        return cls(content=str(data), provider="unknown")
