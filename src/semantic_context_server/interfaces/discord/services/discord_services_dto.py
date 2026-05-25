from dataclasses import dataclass
from typing import Any, Protocol

from semantic_context_server.interfaces.discord.dependencies import IntentClassifierProtocol


class CampaignStateProtocol(Protocol):
    def get(self, key: Any) -> Any: ...
    def set(self, key: Any, value: Any) -> None: ...
    def clear(self, key: Any) -> None: ...


@dataclass
class DiscordServicesDTO:
    campaign_state: CampaignStateProtocol
    intent_classifier: IntentClassifierProtocol
    responder_factory: Any = None
