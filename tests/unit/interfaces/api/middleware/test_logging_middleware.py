from semantic_context_server.interfaces.api.middleware.logging_middleware import (
    log_request_end,
    log_request_start,
)

# ---------------------------------------------------------
# DUMMIES
# ---------------------------------------------------------


class DummyLogger:
    def __init__(self):
        self.messages = []

    def info(self, msg, *args):
        self.messages.append(msg % args)


class DummyRequest:
    method = "GET"

    class url:
        path = "/test"


class DummyResponse:
    status_code = 200


# ---------------------------------------------------------
# TESTES
# ---------------------------------------------------------


def test_log_request_start():
    logger = DummyLogger()

    log_request_start(logger, DummyRequest())

    msg = logger.messages[0]

    assert "request start" in msg
    assert "GET" in msg
    assert "/test" in msg


def test_log_request_end():
    logger = DummyLogger()

    log_request_end(logger, DummyResponse(), 123)

    msg = logger.messages[0]

    assert "request end" in msg
    assert "200" in msg
    assert "123" in msg
