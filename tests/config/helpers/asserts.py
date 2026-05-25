# tests/helpers/response_asserts.py

from semantic_context_server.application.contracts.response import Response


def assert_response(resp):
    assert isinstance(resp, Response)
    assert isinstance(resp.text, str)


def assert_text(resp, expected: str):
    assert_response(resp)
    assert resp.text == expected, f"Expected '{expected}', got '{resp.text}'"


def assert_contains(resp, text: str):
    assert_response(resp)
    assert text in resp.text


def assert_not_empty(resp):
    assert_response(resp)
    assert resp.text.strip() != ""
