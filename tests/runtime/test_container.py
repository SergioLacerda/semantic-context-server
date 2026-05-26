import pytest

from packages.features.llm_gateway.contracts import LLMGatewayContract
from semantic_context_server.application.dto.llm_request import LLMRequest
from tests.config.composition.test_container_builder import ContainerTestFactory
from tests.config.fakes.infrastructure.llm.fake_llm_service import FakeLLMService


async def test_container_builds_core(container):
    campaign = await container.campaigns.get("c1")

    assert container.embedding is not None
    assert campaign.vector_index is not None
    assert isinstance(container.llm, LLMGatewayContract)


def test_container_lazy_loading():
    c = ContainerTestFactory().build()

    first = c.llm
    second = c.llm

    assert first is second


@pytest.mark.asyncio
async def test_usecase_with_fake_llm():
    fake_llm = FakeLLMService(result="ok")

    container = ContainerTestFactory().with_llm(fake_llm).build()
    campaign = await container.campaigns.get("test")

    assert campaign.narrative.llm is fake_llm


async def test_narrative_usecase_wiring(container):
    campaign = await container.campaigns.get("c1")
    usecase = campaign.narrative

    assert usecase is not None
    assert usecase.llm is not None
    assert campaign.vector_index is not None

    assert isinstance(usecase.llm, LLMGatewayContract)


@pytest.mark.asyncio
async def test_llm_integration(container):
    assert isinstance(container.llm, LLMGatewayContract)

    response = await container.llm.generate(LLMRequest(prompt="teste", campaign_id="c1"))

    assert response.content is not None
