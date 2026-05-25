import pytest


@pytest.mark.contract
@pytest.mark.asyncio
async def test_document_store_contract(container_with_storage):
    campaign = await container_with_storage.campaigns.get("c1")

    store = campaign.storage.build_document_store()

    assert store is not None
