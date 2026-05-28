import pytest

from packages.features.rpg_engine.response import Response
from tests.config.fakes.infrastructure.llm.fake_llm_service import FakeLLMService
from tests.config.harness.narrative_harness import NarrativeHarness
from tests.utils.assertions import (
    assert_not_empty,
    assert_semantic,
)


class SpyMemory:
    def __init__(self):
        self.calls = []

    async def append(self, text):
        self.calls.append(text)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_narrative_basic_flow(container):
    result = await container.narrative.execute(
        campaign_id="test",
        user_id="user1",
        action="look around",
    )

    assert isinstance(result, Response)
    assert_not_empty(result)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_narrative_uses_memory(container_factory, monkeypatch):
    spy = SpyMemory()

    root = container_factory()
    campaign_id = "test"
    campaign = await root.campaigns.get(campaign_id)
    await campaign.initialize()

    # 🔥 CORREÇÃO: espionar MemoryService
    monkeypatch.setattr(
        campaign.memory_service,
        "append",
        spy.append,
    )

    usecase = campaign.narrative

    await usecase.execute(campaign_id=campaign_id, user_id="user1", action="open door")
    await usecase.execute(campaign_id=campaign_id, user_id="user1", action="enter room")

    assert len(spy.calls) >= 2


@pytest.mark.unit
@pytest.mark.asyncio
async def test_narrative_llm_failure(container_factory):
    fake = FakeLLMService(fail=True)

    root = container_factory(llm=fake)
    campaign_id = "test"
    campaign = await root.campaigns.get(campaign_id)
    await campaign.initialize()

    result = await campaign.narrative.execute(
        campaign_id=campaign_id,
        user_id="1",
        action="test",
    )

    assert isinstance(result, Response)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_narrative_event_bus_failure(container, monkeypatch):
    def fail(*args, **kwargs):
        raise Exception("event bus failed")

    monkeypatch.setattr(container.event_bus, "publish", fail)

    result = await container.narrative.execute(
        campaign_id="test",
        action="test",
        user_id="user",
    )

    assert isinstance(result, Response)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_narrative_same_input_generates_valid_output(container):
    result1 = await container.narrative.execute(
        campaign_id="test",
        user_id="user",
        action="wait",
    )

    result2 = await container.narrative.execute(
        campaign_id="test",
        user_id="user",
        action="wait",
    )

    assert_not_empty(result1)
    assert_not_empty(result2)


@pytest.mark.asyncio
async def test_narrative_snapshot(container_factory):
    fake_llm = FakeLLMService()

    root = container_factory(llm=fake_llm)
    campaign_id = "test"
    campaign = await root.campaigns.get(campaign_id)
    await campaign.initialize()

    result = await campaign.narrative.execute(
        campaign_id=campaign_id,
        user_id="user",
        action="look around",
    )

    assert_semantic(result, "look", "notice")
    assert_not_empty(result)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_narrative_multi_step_flow(container):
    usecase = container.narrative

    campaign_id = "test"
    await usecase.execute(campaign_id=campaign_id, user_id="u", action="look")
    await usecase.execute(campaign_id=campaign_id, user_id="u", action="walk")

    result = await usecase.execute(campaign_id=campaign_id, user_id="u", action="open door")

    assert_not_empty(result)


@pytest.mark.asyncio
async def test_narrative_multi_campaign(container_factory):
    h = NarrativeHarness()

    r1 = await h.run(
        action="dragon appears",
        campaign_id="c1",
        container_factory=container_factory,
    )

    r2 = await h.run(
        action="spaceship explodes",
        campaign_id="c2",
        container_factory=container_factory,
    )

    assert r1 is not None
    assert r2 is not None

    assert h.records[0]["campaign_id"] == "c1"
    assert h.records[1]["campaign_id"] == "c2"
