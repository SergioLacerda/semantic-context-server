import logging
import time
import uuid
from typing import Any

from fastapi import Request

from semantic_context_server.shared.logging.context import set_request_id

logger = logging.getLogger("semantic_context_server.api")


def _extract_campaign_id(request: Request) -> str | None:
    """Extract the campaign ID from the request path if present.

    Expected path format: /campaign/{campaign_id}/... or /campaign/{campaign_id}
    Returns the campaign ID string or ``None`` if not found or on error.
    """
    try:
        parts = request.url.path.strip("/").split("/")
        if len(parts) >= 2 and parts[0] == "campaign":
            return parts[1]
    except Exception:
        return None
    return None


async def request_context_middleware(request: Request, call_next: Any) -> Any:
    """FastAPI middleware that adds a request ID, logs request lifecycle, and extracts campaign ID.

    - Generates a UUID for each request and stores it in the logging context.
    - Logs the start and end of the request with duration.
    - Makes the ``campaign_id`` available via ``request.state`` for downstream handlers.
    """
    request_id = str(uuid.uuid4())
    set_request_id(request_id)

    start = time.time()

    # Extract and store campaign ID in request.state
    request.state.campaign_id = _extract_campaign_id(request)

    # Log request start
    logger.info(
        "request start method=%s path=%s",
        request.method,
        request.url.path,
    )

    try:
        response = await call_next(request)
        duration = int((time.time() - start) * 1000)
        logger.info(
            "request end status=%s duration_ms=%s",
            response.status_code,
            duration,
        )
        return response
    except Exception:
        logger.exception("request failed")
        raise
