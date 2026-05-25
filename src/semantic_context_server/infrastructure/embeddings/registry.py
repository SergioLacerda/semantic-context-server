# infrastructure/embeddings/registry.py
from collections.abc import Callable
from typing import Any


class EmbeddingRegistry:
    def __init__(self) -> None:
        self._providers: dict[str, Callable[..., Any]] = {}

    def register(self, name: str, factory: Callable[..., Any]) -> None:
        if name in self._providers:
            return

        self._providers[name] = factory

    def create(self, name: str, **kwargs: Any) -> Any:
        if name not in self._providers:
            raise ValueError(
                f"Embedding provider not found: {name}. Available: {list(self._providers.keys())}"
            )

        return self._providers[name](**kwargs)

    def list_providers(self) -> list[str]:
        return list(self._providers.keys())
