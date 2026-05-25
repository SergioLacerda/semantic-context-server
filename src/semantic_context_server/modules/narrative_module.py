from typing import Any

from semantic_context_server.application.ports.llm import LLMServicePort
from semantic_context_server.application.usecases.narrative_event_usecase import NarrativeUseCase
from semantic_context_server.domain.rag.context_builder import ContextBuilder


class NarrativeModule:
    @staticmethod
    def build(container: Any, ctx: Any, services: Any) -> Any:
        memory_service = services["memory"]
        return NarrativeUseCase(
            llm=container.resolve(LLMServicePort),
            memory_service=memory_service,
            context_builder=ContextBuilder(memory_service=memory_service),
        )
