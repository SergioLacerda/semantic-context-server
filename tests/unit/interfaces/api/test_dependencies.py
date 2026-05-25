from types import SimpleNamespace
from typing import Any, cast

import pytest

from semantic_context_server.interfaces.api.dependencies import get_health_service


@pytest.mark.asyncio
async def test_get_health_service_without_container():
    request = SimpleNamespace(app=SimpleNamespace(state=SimpleNamespace()))

    service = await get_health_service(cast(Any, request))

    result = await service.is_ready()

    assert result is True


@pytest.mark.asyncio
async def test_get_health_service_without_health_attr():
    container = SimpleNamespace()

    request = SimpleNamespace(app=SimpleNamespace(state=SimpleNamespace(container=container)))

    service = await get_health_service(cast(Any, request))

    result = await service.is_ready()

    assert result is True
