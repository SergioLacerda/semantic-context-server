from typing import Any

from semantic_context_server.application.ports.model_delegate import ModelDelegatePort


class ExternalModelDelegate(ModelDelegatePort):
    """Delegates model calls to an external API (e.g. OpenAI)."""

    def __init__(self, settings: Any) -> None:
        self._settings = settings

    async def run(self, payload: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError(
            "ExternalModelDelegate.run() not yet implemented. "
            "Wire a concrete LLM provider via the application container."
        )
