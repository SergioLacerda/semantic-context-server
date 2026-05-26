import pytest

from packages.features.llm_gateway.application.error_mapper import map_http_error
from packages.features.llm_gateway.application.llm_errors import (
    LLMClientError,
    LLMRateLimitError,
    LLMRetryableError,
    LLMServerError,
)


@pytest.mark.parametrize("status", [400, 401, 403, 404, 422, 499])
def test_4xx_raises_client_error(status):
    with pytest.raises(LLMClientError) as exc:
        map_http_error(status, "client error")

    assert "client error" in str(exc.value)


@pytest.mark.parametrize("status", [200, 201, 300, 500, 502, 503])
def test_non_4xx_raises_retryable_error(status):
    with pytest.raises(LLMRetryableError) as exc:
        map_http_error(status, "retry")

    assert "retry" in str(exc.value)


def test_boundary_399_not_client_error():
    with pytest.raises(LLMRetryableError):
        map_http_error(399, "edge")


def test_boundary_400_is_client_error():
    with pytest.raises(LLMClientError):
        map_http_error(400, "edge")


def test_message_is_preserved():
    msg = "specific error message"

    with pytest.raises(LLMClientError) as exc:
        map_http_error(400, msg)

    assert str(exc.value) == msg


def test_rate_limit():
    with pytest.raises(LLMRateLimitError):
        map_http_error(429, "too many requests")


def test_quota_exceeded():
    with pytest.raises(LLMClientError) as exc:
        map_http_error(402, "quota")

    assert exc.value.code == "quota_exceeded"


def test_client_error():
    with pytest.raises(LLMClientError):
        map_http_error(404, "not found")


def test_server_error():
    with pytest.raises(LLMServerError):
        map_http_error(500, "server error")


def test_fallback_retryable():
    with pytest.raises(LLMRetryableError) as exc:
        map_http_error(301, "redirect")

    assert "[301]" in str(exc.value)
