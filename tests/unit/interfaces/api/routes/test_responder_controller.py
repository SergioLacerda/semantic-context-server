import pytest
from fastapi.responses import JSONResponse

from semantic_context_server.interfaces.api.api_responder import ApiResponder


@pytest.mark.asyncio
async def test_response_without_send():
    responder = ApiResponder()

    response = responder.response()

    assert isinstance(response, JSONResponse)
    assert response.body == b'{"message":""}'


@pytest.mark.asyncio
async def test_response_with_send():
    responder = ApiResponder()

    await responder.send("hello world")

    response = responder.response()

    assert response.body == b'{"message":"hello world"}'


@pytest.mark.asyncio
async def test_send_overwrites_previous_payload():
    responder = ApiResponder()

    await responder.send("first")
    await responder.send("second")

    response = responder.response()

    assert response.body == b'{"message":"second"}'
