from dataclasses import dataclass


@dataclass
class PlayerActionEvent:
    campaign_id: str
    action: str
    user_id: str
