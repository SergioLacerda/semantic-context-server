from typing import Any


class GMCommand:
    name = "gm"
    description = "Executa ação narrativa"
    usage = "!gm <ação>"
    category = "🎭 Narrativa"
    requires_campaign = True

    def __init__(self, campaign_id: str, user_id: str, action: str):
        self.campaign_id = campaign_id
        self.user_id = user_id
        self.action = action

    # ======================================================
    # BUILDERS
    # ======================================================

    @classmethod
    def from_parsed(cls, parsed: Any, ctx: Any, campaign_id: str) -> "GMCommand":
        return cls(
            campaign_id=campaign_id,
            user_id=str(ctx.author.id),
            action=" ".join(parsed.args),
        )

    @classmethod
    def from_text(cls, text: str, ctx: Any, campaign_id: str) -> "GMCommand":
        return cls(
            campaign_id=campaign_id,
            user_id=str(ctx.author.id),
            action=text,
        )
