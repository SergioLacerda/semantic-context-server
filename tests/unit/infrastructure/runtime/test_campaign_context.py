import pytest

from semantic_context_server.infrastructure.runtime.campaign_context import CampaignContext


def test_set_and_get():
    ctx = CampaignContext()

    ctx.set_campaign("abc")

    assert ctx.get_campaign() == "abc"


def test_get_without_set():
    ctx = CampaignContext()

    ctx.reset()

    with pytest.raises(RuntimeError):
        ctx.get_campaign()


def test_reset_with_token():
    ctx = CampaignContext()

    ctx.reset()

    token = ctx.set_campaign("abc")

    ctx.reset(token)

    with pytest.raises(RuntimeError):
        ctx.get_campaign()


def test_reset_without_token():
    ctx = CampaignContext()

    ctx.set_campaign("abc")
    ctx.reset()

    with pytest.raises(RuntimeError):
        ctx.get_campaign()


def test_scope():
    ctx = CampaignContext()

    with ctx.scope("xyz") as cid:
        assert cid == "xyz"
        assert ctx.get_campaign() == "xyz"

    # saiu do contexto → reset automático
    with pytest.raises(RuntimeError):
        ctx.get_campaign()


def test_context_is_isolated():
    ctx = CampaignContext()

    with ctx.scope("a"):
        assert ctx.get_campaign() == "a"

    with ctx.scope("b"):
        assert ctx.get_campaign() == "b"
