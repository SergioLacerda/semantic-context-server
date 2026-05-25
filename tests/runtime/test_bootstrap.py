import asyncio

import pytest


@pytest.mark.asyncio
async def test_vector_index_bootstrap(container):
    campaign = await container.campaigns.get("c1")

    writer = campaign.vector_writer
    reader = campaign.vector_reader

    assert writer is not None
    assert reader is not None

    # -----------------------------------------------------
    # WRITE
    # -----------------------------------------------------
    await writer.store_event(
        campaign_id="c1",
        texts=["hello"],
        metadata={"test": True},
    )

    # ✔ World Class: Garantir que o flush ocorra se o writer for o serviço de batching
    # Caso contrário, apenas cede o loop para tasks pendentes
    if hasattr(writer, "flush"):
        await writer.flush()
    else:
        await asyncio.sleep(0)

    # -----------------------------------------------------
    # READ
    # -----------------------------------------------------
    result = await reader.search(
        campaign_id="c1",
        query="hello",
        k=1,
    )

    assert isinstance(result, list)
