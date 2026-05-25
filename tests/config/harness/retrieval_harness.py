import asyncio

from tests.config.fakes.infrastructure.retrieval.fake_retrieval import FakeContextWindow
from tests.config.fakes.infrastructure.vector.fake_vector_index import FakeVectorIndex
from tests.config.harness.base_harness import BaseHarness


class DummySelector:
    def select(self, docs):
        return docs[:2]


class RetrievalHarness(BaseHarness):
    def __init__(self, docs=None, campaign_id="test_campaign"):
        super().__init__()

        self.campaign_id = campaign_id

        self.vector_index = FakeVectorIndex()

        docs = docs or ["doc1", "doc2", "doc3"]

        asyncio.run(self.vector_index.add(docs))

        self.selector = DummySelector()
        self.context_window = FakeContextWindow()

    def build(self):
        from semantic_context_server.application.services.retrieval_pipeline import (
            RetrievalService,
        )

        return RetrievalService(
            vector_index=self.vector_index,
            planner=None,
            context_window=self.context_window,
            selector=self.selector,
        )

    async def run(self, query="test"):
        service = self.build()
        result = await service.search(query)

        self.record(query=query, result=result)

        return result
