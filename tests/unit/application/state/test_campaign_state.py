import pytest

from semantic_context_server.application.state.campaign_state import CampaignState

# ---------------------------------------------------------
# FIXTURE
# ---------------------------------------------------------


@pytest.fixture
def state():
    return CampaignState()


# ---------------------------------------------------------
# TESTES
# ---------------------------------------------------------


def test_initial_state_is_empty(state):
    assert state.get("channel_1") is None


def test_get_returns_none_for_unknown_channel(state):
    assert state.get("unknown") is None


def test_set_and_get(state):
    state.set("channel_1", "campaign_a")

    assert state.get("channel_1") == "campaign_a"


def test_set_overwrites_existing_value(state):
    state.set("channel_1", "campaign_a")
    state.set("channel_1", "campaign_b")

    assert state.get("channel_1") == "campaign_b"


def test_instances_are_isolated():
    state1 = CampaignState()
    state2 = CampaignState()

    state1.set("channel_1", "campaign_a")

    assert state2.get("channel_1") is None
