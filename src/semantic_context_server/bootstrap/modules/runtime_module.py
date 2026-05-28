from typing import Any

from packages.core.bootstrap_runtime.runtime_scope import InteractionState
from semantic_context_server.application.ports.interaction_runtime import InteractionRuntimePort


class RuntimeModule:
    def configure(self, container: Any) -> None:
        container.register(InteractionRuntimePort, InteractionState())
