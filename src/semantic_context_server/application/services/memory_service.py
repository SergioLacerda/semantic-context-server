import logging
from typing import Any

from semantic_context_server.application.dto.llm_request import LLMRequest
from semantic_context_server.domain.narrative.narrative_memory import NarrativeMemory

logger = logging.getLogger(__name__)


class MemoryService:
    def __init__(
        self,
        repository: Any,
        campaign_id: str,
        *,
        max_events: int = 10,
        summarizer: Any = None,
        llm_service: Any = None,
        executor: Any = None,
        compressor: Any = None,
        narrative_graph: Any = None,
        vector_reader: Any = None,
        vector_writer: Any = None,
    ) -> None:
        self.repo = repository
        self.campaign_id = campaign_id
        self.max_events = max_events
        self.summarizer = summarizer
        self.llm = llm_service
        self.executor = executor

        self.graph = narrative_graph

        self.vector_reader = vector_reader
        self.vector_writer = vector_writer

        self.compressor = compressor or self._default_compress

    # ==========================================================
    # APPEND (WRITE PATH)
    # ==========================================================

    async def append(self, *args: Any) -> None:
        campaign_id, text = self._parse_append_args(*args)
        text = await self._compress(text)
        if not text:
            return

        memory = await self.load_memory(campaign_id)
        memory.add_event(text)

        await self._update_graph(campaign_id, text)
        await self._update_vector_index(campaign_id, text)
        await self._handle_overflow(memory)

        await self.save_memory(memory, campaign_id)

    async def _compress(self, text: str) -> str:
        if self.executor:
            return str(await self.executor.run(self.compressor, text))
        return str(self.compressor(text))

    async def _update_graph(self, campaign_id: str, text: str) -> None:
        if not self.graph:
            return
        try:
            await self.graph.update_from_event(campaign_id=campaign_id, text=text)
        except Exception:
            logger.warning("Graph update failed", exc_info=True)

    async def _update_vector_index(self, campaign_id: str, text: str) -> None:
        if not self.vector_writer:
            return
        try:
            await self.vector_writer.store_event(campaign_id, [text], {})
        except Exception:
            logger.warning("Failed to queue event for vector indexing", exc_info=True)

    async def _handle_overflow(self, memory: NarrativeMemory) -> None:
        if len(memory.recent_events) <= self.max_events:
            return

        overflow = memory.recent_events[: -self.max_events]
        memory._recent_events = memory.recent_events[-self.max_events :]

        if self.summarizer and len(overflow) >= 3:
            await self._summarize_overflow(memory, overflow)

    async def _summarize_overflow(self, memory: NarrativeMemory, overflow: list[Any]) -> None:
        try:
            items = [{"text": e} for e in overflow]
            if self.executor:
                raw_text = str(await self.executor.run(self.summarizer.extract, items))
            else:
                raw_text = str(self.summarizer.extract(items))

            summary = await self._build_summary(memory, raw_text)
            memory.update_summary(summary)
        except Exception:
            logger.warning("Summarization failed", exc_info=True)

    async def _build_summary(self, memory: NarrativeMemory, raw_text: str) -> str:
        if not self.llm:
            return (memory.summary + "\n" + raw_text).strip()

        if self.executor:
            prompt = str(await self.executor.run(self.summarizer.build_prompt, raw_text))
        else:
            prompt = str(self.summarizer.build_prompt(raw_text))

        request = LLMRequest(
            prompt=prompt,
            campaign_id=self.campaign_id,
            system_prompt="",
            temperature=0.3,
            max_tokens=300,
        )
        response = await self.llm.generate(request)
        return response.content if response else memory.summary

    # ==========================================================
    # READ PATH (🔥 RAG REAL)
    # ==========================================================

    async def get_context(self, query: str | None = None, **kwargs: Any) -> dict[str, Any]:
        campaign_id = str(kwargs.get("campaign_id") or self.campaign_id)
        query_text = str(kwargs.get("query") or query or "")
        memory = await self.load_memory(campaign_id)

        result = {
            "summary": memory.summary,
            "recent": memory.recent_events[-5:],
        }

        # -----------------------------------------------------
        # VECTOR (SEMANTIC RETRIEVAL)
        # -----------------------------------------------------
        if self.vector_reader:
            try:
                docs = await self.vector_reader.search(
                    campaign_id=campaign_id,
                    query=query_text,
                    k=5,
                )

                texts = [d["text"] for d in docs if d.get("text")]

                result["vector"] = texts
                result["semantic"] = texts

            except Exception:
                logger.warning("Vector retrieval failed", exc_info=True)
                result["vector"] = []

        # -----------------------------------------------------
        # GRAPH
        # -----------------------------------------------------
        if self.graph:
            try:
                result["graph"] = await self.graph.search(
                    campaign_id=campaign_id,
                    query=query_text,
                )
            except Exception:
                logger.warning("Graph search failed", exc_info=True)
                result["graph"] = []

        return result

    # ==========================================================
    # STORAGE
    # ==========================================================

    async def load_memory(self, campaign_id: str | None = None) -> NarrativeMemory:
        cid = campaign_id or self.campaign_id
        data = await self.repo.load(cid)

        if not data:
            return NarrativeMemory()

        result: NarrativeMemory = NarrativeMemory.from_dict(data)
        return result

    async def save_memory(self, memory: NarrativeMemory, campaign_id: str | None = None) -> None:
        cid = campaign_id or self.campaign_id
        await self.repo.save(cid, memory.to_dict())

    async def clear(self, campaign_id: str | None = None) -> None:
        await self.save_memory(self.create_empty(), campaign_id)

    # ==========================================================
    # UTILS
    # ==========================================================

    def create_empty(self) -> NarrativeMemory:
        return NarrativeMemory()

    def _default_compress(self, text: str) -> str:
        if not text:
            return text

        text = text.strip()

        if len(text) > 200:
            return text[:200].rsplit(" ", 1)[0]

        return text

    def _parse_append_args(self, *args: Any) -> tuple[str, str]:
        if len(args) == 1:
            return self.campaign_id, str(args[0])
        if len(args) >= 2:
            return str(args[0]), str(args[1])
        raise TypeError("append() expects (text) or (campaign_id, text)")
