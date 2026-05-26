import pytest

from packages.features.vector_index.contracts import VectorWriterPort
from tests.contracts.framework.rules.port_compliance_rule import ensure_port_compliance


@pytest.mark.contract
@pytest.mark.asyncio
async def test_vector_writer_contract(container):
    campaign = await container.campaigns.get("test")

    writer = campaign.vector_writer

    ensure_port_compliance(writer, VectorWriterPort)

    await writer.store_event(
        campaign_id="c1",
        texts=["hello"],
        metadata={"test": True},
    )
