from dataclasses import dataclass
from unittest.mock import AsyncMock

from tests.config.fakes.application.usecases.fake_usecases import (
    DummyEndSession,
    DummyNarrative,
    DummyRoll,
)
from tests.config.fakes.domain.state.campaign_state import (
    DummyCampaignState,
)


@dataclass
class DummyCampaignContainer:
    """Represents a campaign-scoped container with use cases."""

    narrative: object
    roll_dice: object
    end_session: object
    intent_classifier: object | None


@dataclass
class TestDeps:
    narrative: object
    roll_dice: object
    end_session: object
    campaign_state: object
    intent_classifier: object | None
    create_campaign: object
    list_campaigns: object
    delete_campaign: object
    resolve_campaign: object


def make_deps(**overrides):
    base = TestDeps(
        narrative=DummyNarrative(),
        roll_dice=DummyRoll(),
        end_session=DummyEndSession(),
        campaign_state=DummyCampaignState("test_campaign"),
        intent_classifier=None,
        create_campaign=AsyncMock(return_value="ok"),
        list_campaigns=AsyncMock(return_value=["test_campaign"]),
        delete_campaign=AsyncMock(return_value=True),
        resolve_campaign=None,
    )

    for k, v in overrides.items():
        setattr(base, k, v)

    if "resolve_campaign" not in overrides:

        async def _resolve_campaign(campaign_id: str):
            return DummyCampaignContainer(
                narrative=base.narrative,
                roll_dice=base.roll_dice,
                end_session=base.end_session,
                intent_classifier=base.intent_classifier,
            )

        base.resolve_campaign = _resolve_campaign

    return base
