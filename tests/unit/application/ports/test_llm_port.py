import pytest

from packages.features.llm_gateway.contracts import LLMGatewayContract
from tests.config.fakes.infrastructure.llm.fake_llm_request_factory import FakeLLMRequestFactory


@pytest.mark.contract
@pytest.mark.asyncio
async def test_llm_port_contract(container):
    llm = container.llm

    assert isinstance(llm, LLMGatewayContract)

    result = await llm.generate(FakeLLMRequestFactory.simple("hello"))

    assert result is not None
    assert hasattr(result, "content")
    assert isinstance(result.content, str)
