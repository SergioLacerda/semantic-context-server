import pytest


@pytest.mark.slow
@pytest.mark.integration
@pytest.mark.asyncio
async def test_storage_set_get(container_with_storage):
    container = container_with_storage

    campaign = await container.campaigns.get("c1")

    store = campaign.storage.build_document_store()

    await store.set("doc1", {"x": 1})

    assert (await store.get("doc1"))["x"] == 1


@pytest.mark.slow
@pytest.mark.integration
@pytest.mark.asyncio
async def test_storage_isolation(container_with_storage):
    container = container_with_storage

    c1 = await container.campaigns.get("c1")
    c2 = await container.campaigns.get("c2")

    await c1.storage.build_document_store().set("a", {"v": 1})

    assert await c2.storage.build_document_store().get("a") is None
