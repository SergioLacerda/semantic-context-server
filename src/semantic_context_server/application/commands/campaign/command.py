from typing import Any


class CampaignCommand:
    command_name = "campaign"
    description = "Gerencia campanhas"
    usage = "!campaign <action> [name]"
    category = "🎭 Campanha"
    requires_campaign = False

    action: str | None
    name: str | None
    user_id: str | None
    campaign_id: str | None

    def __init__(
        self,
        action: str | None,
        name: str | None,
        user_id: str | None,
        campaign_id: str | None = None,
    ):
        self.action = action
        self.name = name
        self.user_id = user_id
        self.campaign_id = campaign_id

    # ======================================================
    # BUILDERS
    # ======================================================

    @classmethod
    def from_parsed(cls, parsed: Any, ctx: Any, campaign_id: str | None) -> "CampaignCommand":
        args = parsed.args

        action = args[0] if args else None
        name = args[1] if len(args) > 1 else None

        return cls(
            action=action,
            name=name,
            user_id=str(ctx.author.id),
            campaign_id=campaign_id,
        )
