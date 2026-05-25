import asyncio

import pytest

# ==========================================================
# 🔥 CONTAINER START / SHUTDOWN
# ==========================================================


@pytest.mark.asyncio
async def test_container_start_shutdown(container_factory):
    c = container_factory(campaign_id="c1")

    await c.start()

    campaign = await c.campaigns.get("c1")
    assert campaign is not None

    await c.shutdown()

    if hasattr(c, "_lifecycle_guard"):
        c._lifecycle_guard.assert_clean()


# ==========================================================
# 🔥 IDEMPOTÊNCIA
# ==========================================================


@pytest.mark.asyncio
async def test_container_start_idempotent(container_factory):
    c = container_factory()

    await c.start()
    await c.start()

    await c.shutdown()


@pytest.mark.asyncio
async def test_container_shutdown_idempotent(container_factory):
    c = container_factory()

    await c.start()
    await c.shutdown()
    await c.shutdown()


# ==========================================================
# 🔥 CONCORRÊNCIA (CRÍTICO)
# ==========================================================


@pytest.mark.asyncio
async def test_campaign_container_concurrency(container):
    async def get():
        return await container.campaigns.get("c1")

    results = await asyncio.gather(*[get() for _ in range(20)])

    ids = {id(r) for r in results}
    assert len(ids) == 1


# ==========================================================
# 🔥 MULTI-CAMPAIGN ISOLATION
# ==========================================================


@pytest.mark.asyncio
async def test_campaign_isolation_deep(container_factory):
    c = container_factory()
    await c.start()

    c1 = await c.campaigns.get("c1")
    c2 = await c.campaigns.get("c2")

    assert c1 is not c2

    # storage
    assert c1.storage is not c2.storage

    # caches
    assert c1.embedding_cache is not c2.embedding_cache
    assert c1.semantic_cache is not c2.semantic_cache

    # vector (🔥 NOVO PADRÃO)
    assert c1.vector_writer is not c2.vector_writer
    assert c1.vector_reader is not c2.vector_reader

    await c.shutdown()


# ==========================================================
# 🔥 VECTOR WRITER — DRAIN + SHUTDOWN
# ==========================================================


@pytest.mark.asyncio
async def test_vector_writer_shutdown_drain(container_factory):
    c = container_factory()
    await c.start()

    campaign = await c.campaigns.get("c1")
    writer = campaign.vector_writer

    # enqueue eventos
    for i in range(50):
        await writer.store_event("c1", [f"text {i}"], {})

    # shutdown deve drenar sem erro
    await c.shutdown()

    if hasattr(c, "_lifecycle_guard"):
        c._lifecycle_guard.assert_clean()


# ==========================================================
# 🔥 CLEANUP LOOP (TTL / LRU)
# ==========================================================


@pytest.mark.asyncio
async def test_campaign_cleanup(container_factory):
    c = container_factory()
    await c.start()

    c1 = await c.campaigns.get("c1")
    c2 = await c.campaigns.get("c2")

    assert c1 is not None
    assert c2 is not None

    await c.campaigns.clear("c1")

    c1_new = await c.campaigns.get("c1")

    assert c1_new is not c1

    await c.shutdown()


# ==========================================================
# 🔥 SHUTDOWN COMPLETO (CRÍTICO)
# ==========================================================


@pytest.mark.asyncio
async def test_container_shutdown_cleans_everything(container_factory):
    c = container_factory()
    await c.start()

    campaigns = await asyncio.gather(*[c.campaigns.get(f"c{i}") for i in range(5)])

    assert len(campaigns) == 5

    await c.shutdown()

    if hasattr(c, "_lifecycle_guard"):
        c._lifecycle_guard.assert_clean()


# ==========================================================
# 🔥 RESTART (ROBUSTEZ)
# ==========================================================


@pytest.mark.asyncio
async def test_container_restart(container_factory):
    c = container_factory()

    await c.start()
    await c.campaigns.get("c1")

    await c.shutdown()

    await c.start()
    campaign2 = await c.campaigns.get("c1")

    assert campaign2 is not None

    await c.shutdown()


# ==========================================================
# 🔥 ERROR SAFETY
# ==========================================================


@pytest.mark.asyncio
async def test_campaign_creation_error_does_not_lock(container_factory):
    c = container_factory()
    await c.start()

    async def create():
        return await c.campaigns.get("c1")

    results = await asyncio.gather(
        *[create() for _ in range(10)],
        return_exceptions=True,
    )

    assert all(not isinstance(r, Exception) for r in results)

    await c.shutdown()


# ==========================================================
# 🔥 MASSIVE LOAD (STRESS LIGHT)
# ==========================================================


@pytest.mark.asyncio
async def test_campaign_mass_creation(container_factory):
    c = container_factory()
    await c.start()

    async def create(i):
        return await c.campaigns.get(f"c{i}")

    results = await asyncio.gather(*[create(i) for i in range(30)])

    assert len(results) == 30

    await c.shutdown()

    if hasattr(c, "_lifecycle_guard"):
        c._lifecycle_guard.assert_clean()
