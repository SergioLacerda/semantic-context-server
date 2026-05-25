from typing import Any


def log_request_start(logger: Any, request: Any) -> None:
    logger.info(
        "request start method=%s path=%s",
        request.method,
        request.url.path,
    )


def log_request_end(logger: Any, response: Any, duration: Any) -> None:
    logger.info(
        "request end status=%s duration_ms=%s",
        response.status_code,
        duration,
    )
