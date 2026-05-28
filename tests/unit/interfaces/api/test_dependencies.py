from types import SimpleNamespace
from typing import Any, cast

import pytest

from packages.core.bootstrap_runtime.contracts.service_graph import ServiceGraph
from packages.features.llm_gateway.contracts import LLMGatewayContract
from semantic_context_server.application.ports.event_bus import EventBus
from semantic_context_server.application.ports.executor import ExecutorPort
from semantic_context_server.interfaces.api.dependencies import (
    get_event_bus,
    get_executor,
    get_health_service,
    get_llm,
)


@pytest.mark.asyncio
async def test_get_health_service_without_container():
    request = SimpleNamespace(app=SimpleNamespace(state=SimpleNamespace()))

    service = await get_health_service(cast(Any, request))

    result = await service.is_ready()

    assert result is True


@pytest.mark.asyncio
async def test_get_health_service_without_health_attr():
    container = SimpleNamespace(vector_index=SimpleNamespace())

    request = SimpleNamespace(
        state=SimpleNamespace(container=container),
        app=SimpleNamespace(state=SimpleNamespace(container=container)),
    )

    service = await get_health_service(cast(Any, request))

    result = await service.is_ready()

    assert result is True


@pytest.mark.asyncio
async def test_graph_first_resolution_for_global_dependencies():
    graph = ServiceGraph()

    class _Exec:
        async def shutdown(self) -> None:
            return None

    class _Bus:
        def publish(self, event: object) -> None:  # pragma: no cover
            _ = event

        def subscribe(self, event_type: type, handler: Any) -> None:  # pragma: no cover
            _ = (event_type, handler)

    class _LLM:
        async def generate(self, request: Any) -> Any:  # pragma: no cover
            _ = request
            return None

    exec_inst = _Exec()
    bus_inst = _Bus()
    llm_inst = _LLM()

    graph.register(ExecutorPort, exec_inst)
    graph.register(EventBus, bus_inst)
    graph.register(LLMGatewayContract, llm_inst)

    request = SimpleNamespace(
        app=SimpleNamespace(state=SimpleNamespace(service_graph=graph)),
        state=SimpleNamespace(),
    )

    assert await get_executor(cast(Any, request)) is exec_inst
    assert await get_event_bus(cast(Any, request)) is bus_inst
    assert await get_llm(cast(Any, request)) is llm_inst
