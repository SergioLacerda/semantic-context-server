import logging
from typing import Any

from semantic_context_server.application.dto.llm_request import LLMRequest
from semantic_context_server.domain.narrative.session_summarizer import SessionSummarizer

logger = logging.getLogger(__name__)


class EndSessionUseCase:
    def __init__(
        self, memory_service: Any, llm: Any, vector_writer: Any, executor: Any = None
    ) -> None:
        self.memory = memory_service
        self.llm = llm
        self.vector_writer = vector_writer
        self.executor = executor

        self.summarizer = SessionSummarizer()

    def _fallback_summary(self, text: str) -> str:
        return text[:500].strip()

    async def execute(self, campaign_id: str) -> str:
        memory = await self.memory.load_memory(campaign_id)
        events = memory.recent_events

        if not events:
            return "Nenhum evento ocorreu nesta sessão."

        # 1. Extração via Executor (CPU-bound/List processing)
        event_list = [{"text": e} for e in events]
        if self.executor:
            text = await self.executor.run(self.summarizer.extract, event_list)
        else:
            text = self.summarizer.extract(event_list)

        if not text.strip():
            return "A sessão terminou sem eventos relevantes."

        if self.executor:
            prompt = await self.executor.run(self.summarizer.build_prompt, text)
        else:
            prompt = self.summarizer.build_prompt(text)

        try:
            response = await self.llm.generate(
                LLMRequest(
                    prompt=prompt,
                    campaign_id=campaign_id,
                )
            )
            summary = response.content if response and response.content else ""
        except Exception:
            logger.warning("LLM summarization failed during end_session", exc_info=True)
            summary = self._fallback_summary(text)

        if not summary.strip():
            summary = self._fallback_summary(text)

        # 2. Persistência e Limpeza
        await self.memory.clear(campaign_id)

        # Não usamos create_task aqui; o VectorWriter já tem sua própria fila e worker.
        # Await garante que o evento entre na fila antes de retornarmos.
        await self.vector_writer.store_event(
            campaign_id=campaign_id,
            texts=[summary],
            metadata={"type": "session_summary"},
        )

        return summary
