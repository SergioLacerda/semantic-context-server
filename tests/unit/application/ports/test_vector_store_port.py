import pytest

from semantic_context_server.application.ports.storage import VectorStorePort


@pytest.mark.contract
@pytest.mark.asyncio
async def test_vector_store_contract(vector_store):
    assert isinstance(vector_store, VectorStorePort)

    await vector_store.add("a", [1.0, 0.0], {})

    assert await vector_store.get("a") == [1.0, 0.0]

    result = await vector_store.search([1.0, 0.0], k=1)

    assert isinstance(result, list)

    await vector_store.clear()
