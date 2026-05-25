import pytest

from semantic_context_server.application.ports.llm import LLMServicePort
from tests.config.fakes.infrastructure.llm.fake_llm_request_factory import FakeLLMRequestFactory


@pytest.mark.contract
@pytest.mark.asyncio
async def test_llm_port_contract(container):
    llm = container.llm

    assert isinstance(llm, LLMServicePort)

    result = await llm.generate(FakeLLMRequestFactory.simple("hello"))

    assert result is not None
    assert hasattr(result, "content")
    assert isinstance(result.content, str)
