import pytest
from starlette.responses import Response

from semantic_context_server.interfaces.api.middleware.request_context_middleware import (
    request_context_middleware,
)


class DummyRequest:
    method = "GET"

    class url:
        path = "/test"


@pytest.mark.asyncio
async def test_request_context_success(monkeypatch):
    async def call_next(request):
        return Response(status_code=200)

    request = DummyRequest()

    response = await request_context_middleware(request, call_next)

    assert response.status_code == 200
