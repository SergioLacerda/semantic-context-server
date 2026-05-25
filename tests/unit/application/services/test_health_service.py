import pytest

from semantic_context_server.application.services.health_service import HealthService


class DummyContainer:
    def __init__(self, vector_index, embedding=None, storage=None):
        self.vector_index = vector_index
        self.embedding = embedding or object()
        self.storage = storage or object()


class NoEnsureIndex:
    pass


class SyncEnsureIndex:
    def __init__(self):
        self.called = False

    def ensure_ann_ready(self):
        self.called = True


class AsyncEnsureIndex:
    def __init__(self):
        self.called = False

    async def ensure_ann_ready(self):
        self.called = True


class FailingIndex:
    def ensure_ann_ready(self):
        raise Exception("fail")


def test_is_alive():
    service = HealthService(container=None)

    assert service.is_alive() is True


@pytest.mark.asyncio
async def test_is_ready_without_method():
    container = DummyContainer(NoEnsureIndex())

    service = HealthService(container)

    assert await service.is_ready() is True


@pytest.mark.asyncio
async def test_is_ready_with_sync_method():
    index = SyncEnsureIndex()
    container = DummyContainer(index)

    service = HealthService(container)

    result = await service.is_ready()

    assert result is True
    assert index.called is True


@pytest.mark.asyncio
async def test_is_ready_with_async_method():
    index = AsyncEnsureIndex()
    container = DummyContainer(index)

    service = HealthService(container)

    result = await service.is_ready()

    assert result is True
    assert index.called is True


@pytest.mark.asyncio
async def test_is_ready_failure():
    container = DummyContainer(FailingIndex())

    service = HealthService(container)

    result = await service.is_ready()

    assert result is False


@pytest.mark.asyncio
async def test_status_ready():
    container = DummyContainer(NoEnsureIndex())

    service = HealthService(container)

    result = await service.status()

    assert result["status"] == "ready"
    assert result["components"]["vector_index"] == "ok"


@pytest.mark.asyncio
async def test_status_not_ready():
    container = DummyContainer(FailingIndex())

    service = HealthService(container)

    result = await service.status()

    assert result["status"] == "loading"
    assert result["components"]["vector_index"] == "loading"


@pytest.mark.asyncio
async def test_status_component_types():
    class Embedding:
        pass

    class Storage:
        pass

    container = DummyContainer(
        vector_index=NoEnsureIndex(),
        embedding=Embedding(),
        storage=Storage(),
    )

    service = HealthService(container)

    result = await service.status()

    assert result["components"]["embedding"] == "Embedding"
    assert result["components"]["storage"] == "Storage"
