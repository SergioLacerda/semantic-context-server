from typing import Any

from packages.features.llm_gateway.contracts import LLMGatewayContract
from packages.features.rpg_engine import NarrativeUseCase
from semantic_context_server.domain.rag.context_builder import ContextBuilder


class NarrativeModule:
    @staticmethod
    def build(container: Any, ctx: Any, services: Any) -> Any:
        memory_service = services["memory"]
        return NarrativeUseCase(
            llm=container.resolve(LLMGatewayContract),
            memory_service=memory_service,
            context_builder=ContextBuilder(memory_service=memory_service),
        )
