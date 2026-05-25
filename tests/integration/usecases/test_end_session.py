import pytest

# ==========================================================
# HELPERS
# ==========================================================


async def get_campaign(container, cid="c1"):
    return await container.campaigns.get(cid)


@pytest.mark.asyncio
async def test_end_session_basic(container):
    campaign = await get_campaign(container)

    result = await campaign.end_session.execute("c1")

    assert result is not None
    assert isinstance(result, str)
    assert len(result) > 0


@pytest.mark.asyncio
async def test_end_session_clears_memory(container):
    campaign = await get_campaign(container)

    # simula eventos
    await campaign.memory_service.append("c1", "evento 1")
    await campaign.memory_service.append("c1", "evento 2")

    await campaign.end_session.execute("c1")

    memory = await campaign.memory_service.load_memory("c1")

    assert memory.get_recent_events() == []


@pytest.mark.asyncio
async def test_end_session_index_failure(container, monkeypatch):
    campaign = await get_campaign(container)

    async def fail(*args, **kwargs):
        raise RuntimeError("vector fail")

    monkeypatch.setattr(
        campaign.vector_writer,
        "store_event",
        fail,
    )

    result = await campaign.end_session.execute("c1")

    assert result is not None


@pytest.mark.asyncio
async def test_end_session_llm_edge_cases(container, monkeypatch):
    campaign = await get_campaign(container)

    class FakeLLM:
        async def generate(self, *args, **kwargs):
            class R:
                content = "   "

            return R()

    monkeypatch.setattr(
        campaign.end_session,
        "llm",
        FakeLLM(),
    )

    result = await campaign.end_session.execute("c1")

    assert result is not None
    assert isinstance(result, str)
