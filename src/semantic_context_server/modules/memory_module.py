from typing import Any

from packages.features.llm_gateway.contracts import LLMGatewayContract
from packages.features.prompt_engine_core.session_summarizer import SessionSummarizer
from semantic_context_server.application.ports.executor import ExecutorPort
from semantic_context_server.application.services.memory_service import MemoryService
from semantic_context_server.infrastructure.storage.repositories.narrative_memory_repository import (
    NarrativeMemoryRepository,
)


class MemoryModule:
    @staticmethod
    def build(container: Any, ctx: Any, services: Any) -> Any:
        kv_backend = ctx.kv
        if hasattr(kv_backend, "build_kv_store"):
            kv_store = kv_backend.build_kv_store("narrative_memory")
        else:
            kv_store = kv_backend.build_document_store()

        repo = NarrativeMemoryRepository(kv_store)

        return MemoryService(
            repository=repo,
            campaign_id=ctx.id,
            summarizer=SessionSummarizer(),
            llm_service=container.resolve(LLMGatewayContract),
            executor=container.resolve(ExecutorPort),
            vector_reader=services.get("vector_reader"),
            vector_writer=services.get("vector_writer"),
            narrative_graph=services.get("narrative_graph"),
        )
