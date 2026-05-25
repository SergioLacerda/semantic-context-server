from typing import Any

from semantic_context_server.application.ports.interaction_runtime import InteractionRuntimePort
from semantic_context_server.infrastructure.runtime.interaction_state import InteractionState


class RuntimeModule:
    def configure(self, container: Any) -> None:
        container.register(InteractionRuntimePort, InteractionState())
