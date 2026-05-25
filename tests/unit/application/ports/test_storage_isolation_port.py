import pytest


@pytest.mark.contract
@pytest.mark.asyncio
async def test_storage_isolation(container_with_storage):
    c1 = await container_with_storage.campaigns.get("c1")
    c2 = await container_with_storage.campaigns.get("c2")

    await c1.storage.build_document_store().set("a", {"v": 1})

    assert await c2.storage.build_document_store().get("a") is None
