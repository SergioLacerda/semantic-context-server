import pytest

from packages.features.embedding_gateway.contracts import (
    EmbeddingGatewayContract as EmbeddingGateway,
)
from tests.contracts.framework.rules.port_compliance_rule import ensure_port_compliance


class DummyEmbeddingGateway(EmbeddingGateway):
    async def embed(self, text: str) -> list[float]:
        return [1.0]

    @property
    def dimension(self) -> int | None:
        return 1

    @property
    def supports_batch(self) -> bool:
        return False


@pytest.mark.contract
def test_embedding_gateway_contract():
    gateway = DummyEmbeddingGateway()

    ensure_port_compliance(gateway, EmbeddingGateway)
