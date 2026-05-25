import pytest


@pytest.mark.contract
@pytest.mark.asyncio
async def test_vector_contract(vector_store):
    await vector_store.add("a", [1, 0])

    result = await vector_store.get("a")
    assert result == [1, 0]

    result = await vector_store.search([1, 0], k=1)

    assert isinstance(result, list)

    await vector_store.clear()
