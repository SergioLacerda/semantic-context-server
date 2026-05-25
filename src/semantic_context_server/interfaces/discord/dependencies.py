from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any, Protocol

from semantic_context_server.application.usecases.create_campaign_usecase import (
    CreateCampaignUseCase,
)
from semantic_context_server.application.usecases.list_campaigns_usecase import ListCampaignsUseCase

# =========================================================
# USE CASE PROTOCOLS
# =========================================================


class NarrativeUseCase(Protocol):
    async def execute(self, campaign_id: str, action: str, user_id: str) -> Any: ...


class RollUseCase(Protocol):
    async def execute(self, expression: str) -> Any: ...


class EndSessionUseCase(Protocol):
    async def execute(self, campaign_id: str) -> Any: ...


# =========================================================
# SERVICES PROTOCOLS
# =========================================================


class CampaignStateProtocol(Protocol):
    def get(self, channel_id: str) -> str | None: ...
    def set(self, channel_id: str, campaign_id: str) -> None: ...
    def clear(self, channel_id: str) -> None: ...


class IntentClassifierProtocol(Protocol):
    async def classify(self, text: str, campaign_id: str) -> Any: ...


# =========================================================
# USE CASES (CAMPAIGN)
# =========================================================


class DeleteCampaignUseCase(Protocol):
    async def execute(self, campaign_id: str) -> bool: ...


# =========================================================
# CAMPAIGN CONTAINER CONTRACT
# =========================================================
class CampaignContainerProtocol(Protocol):
    narrative: NarrativeUseCase
    roll_dice: RollUseCase
    end_session: EndSessionUseCase
    intent_classifier: IntentClassifierProtocol


# =========================================================
# DEPENDENCIES OBJECT
# =========================================================


@dataclass
class CommandDependencies:
    # 🔥 resolvers
    resolve_campaign: Callable[[str], Awaitable[CampaignContainerProtocol]]

    # 🔥 state
    campaign_state: CampaignStateProtocol

    # 🔥 queries
    list_campaigns: ListCampaignsUseCase

    # 🔥 commands (faltava isso)
    create_campaign: CreateCampaignUseCase
