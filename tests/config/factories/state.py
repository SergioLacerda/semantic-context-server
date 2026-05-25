# tests/config/factories/state.py

from dataclasses import dataclass
from typing import Any

from tests.config.fakes.application.context.fake_context_service import FakeContextService
from tests.config.fakes.application.intent.fake_intent_classifier import FakeIntentClassifier
from tests.config.fakes.application.memory.fake_application_memory_service import (
    FakeApplicationMemoryService,
)
from tests.config.fakes.infrastructure.embedding.fake_embedding_provider import (
    FakeEmbeddingProvider,
)
from tests.config.fakes.infrastructure.llm.fake_llm_service import FakeLLMService


@dataclass(frozen=True)
class _State:
    campaign_id: str

    llm: FakeLLMService
    embedding: FakeEmbeddingProvider

    context: FakeContextService
    memory: FakeApplicationMemoryService
    intent: FakeIntentClassifier

    base_path: str

    time_provider: Any
    executor: Any | None = None
