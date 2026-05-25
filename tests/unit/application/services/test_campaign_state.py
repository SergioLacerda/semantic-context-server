from semantic_context_server.application.state.campaign_state import CampaignState


def test_initial_state():
    state = CampaignState()

    assert state.get("ch1") is None


def test_set_and_get():
    state = CampaignState()

    state.set("ch1", "camp1")

    assert state.get("ch1") == "camp1"


def test_overwrite_campaign():
    state = CampaignState()

    state.set("ch1", "camp1")
    state.set("ch1", "camp2")

    assert state.get("ch1") == "camp2"


def test_clear_existing():
    state = CampaignState()

    state.set("ch1", "camp1")
    state.clear("ch1")

    assert state.get("ch1") is None


def test_clear_non_existing():
    state = CampaignState()

    state.clear("ch1")

    assert state.get("ch1") is None
