from types import SimpleNamespace

import pytest

from semantic_context_server.application.contracts.response import Response
from semantic_context_server.application.services.message_service import MessageService
from semantic_context_server.infrastructure.runtime.execution.executor import Executor
from semantic_context_server.infrastructure.runtime.interaction_state import InteractionState
from tests.config.factories.framework.context import make_context


class DummyIntentClassifier:
    async def classify(self, content, campaign_id):
        return "ACTION"


class DummyNarrative:
    async def execute(self, campaign_id, action, user_id):
        return Response(text="ok", type="narrative")


class DummyCampaign:
    def __init__(self):
        self.intent_classifier = DummyIntentClassifier()
        self.narrative = DummyNarrative()


class DummyDeps:
    def __init__(self, campaign_state, campaign):
        self.campaign_state = campaign_state
        self._campaign = campaign

    async def resolve_campaign(self, campaign_id):
        return self._campaign


class DummyCampaignState:
    def __init__(self, data):
        self.data = data

    async def get(self, channel_id):
        return self.data.get(channel_id)


@pytest.mark.asyncio
async def test_message_service_integration_with_runtime_port():
    ctx = make_context(user_id="user1", channel_id="channel1")
    message = SimpleNamespace(content="attack", author=SimpleNamespace(bot=False))

    executor = Executor()
    interaction_state = InteractionState()
    campaign_state = DummyCampaignState({"channel1": "camp1"})
    campaign = DummyCampaign()
    deps = DummyDeps(campaign_state, campaign)
    settings = SimpleNamespace()

    service = MessageService(
        deps=deps,
        executor=executor,
        interaction_state=interaction_state,
        settings=settings,
    )

    await service.handle(message, ctx, ctx)

    assert ctx.sent_messages == ["ok"]

    await executor.shutdown()
