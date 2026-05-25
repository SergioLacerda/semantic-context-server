from typing import Any

from semantic_context_server.application.ports.model_delegate import ModelDelegatePort


class LocalModelDelegate(ModelDelegatePort):
    """Delegates model calls to a locally-loaded model."""

    def __init__(self, settings: Any) -> None:
        self._settings = settings

    async def run(self, payload: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError(
            "LocalModelDelegate.run() not yet implemented. "
            "Wire a concrete local model loader via the application container."
        )
