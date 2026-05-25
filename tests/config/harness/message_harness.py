from typing import Any
from unittest.mock import AsyncMock

from semantic_context_server.application.contracts.response import Response
from semantic_context_server.application.services.message_service import MessageService
from tests.config.factories.framework.context import make_context
from tests.config.fakes.application.intent.fake_intent_classifier import FakeIntentClassifier
from tests.config.fakes.domain.state.campaign_state import DummyCampaignState
from tests.config.fakes.framework.runtime import DummyRuntime
from tests.config.helpers.discord_factory import (
    DummyExecutor,
    DummyUsecase,
)


class MessageHarness:
    def __init__(
        self,
        *,
        campaign_id="camp1",
        response: Any = "ok",
        intent="ACTION",
        cooldown=True,
        locked=False,
    ):
        # ---------------------------------------
        # CONTEXT
        # ---------------------------------------
        self.ctx = make_context(guild_id=None, user_id="999")
        self.sent = self.ctx.sent_messages
        self.message_content = "attack"

        # ---------------------------------------
        # STATE
        # ---------------------------------------
        self.campaign_id = campaign_id
        self.campaign_state = DummyCampaignState()

        # Ensure campaign_state.get is async as expected by MessageService
        self.campaign_state.get = AsyncMock(side_effect=self.campaign_state.get)

        if self.campaign_id:
            self.campaign_state.set(
                self.ctx.channel.id,
                self.campaign_id,
            )

        # ---------------------------------------
        # RESPONSE
        # ---------------------------------------
        response_obj = Response(
            text=response or "",
            type="narrative",
            metadata={},
        )

        # ---------------------------------------
        # DEPENDENCIES
        # ---------------------------------------
        self.usecases: Any = type(
            "Usecases",
            (),
            {
                "narrative": DummyUsecase(result=response_obj),
            },
        )()

        self.executor: Any = DummyExecutor()
        self.runtime: Any = DummyRuntime(cooldown=cooldown, locked=locked)
        self.intent = FakeIntentClassifier(intent)

        # Ensure classify is async
        self.intent.classify = AsyncMock(side_effect=self.intent.classify)

        # ---------------------------------------
        # DEPS (Container)
        # ---------------------------------------
        self.deps: Any = type(
            "Deps",
            (),
            {
                "campaign_state": self.campaign_state,
                "resolve_campaign": AsyncMock(
                    return_value=type(
                        "Campaign",
                        (),
                        {"intent_classifier": self.intent, "narrative": self.usecases.narrative},
                    )()
                ),
            },
        )()

        # settings mínimo
        self.settings: Any = type("Settings", (), {})()

    # ---------------------------------------------------------
    # HELPERS
    # ---------------------------------------------------------

    def message(self, content: str):
        self.message_content = content
        return self

    # ---------------------------------------------------------
    # BUILD
    # ---------------------------------------------------------

    def build(self):
        return MessageService(
            deps=self.deps,
            executor=self.executor,
            interaction_state=self.runtime,
            settings=self.settings,
        )

    # ---------------------------------------------------------
    # EXECUTE
    # ---------------------------------------------------------

    async def run(self):
        msg = type(
            "Msg",
            (),
            {
                "content": self.message_content,
                "author": type("Author", (), {"bot": False}),
            },
        )()

        service = self.build()

        # 🔥 responder = ctx (como seus testes usam)
        await service.handle(msg, self.ctx, self.ctx)

        return self.sent
