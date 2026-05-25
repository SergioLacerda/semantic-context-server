from semantic_context_server.application.services.llm.llm_errors import (
    LLMClientError,
    LLMRateLimitError,
    LLMRetryableError,
    LLMServerError,
)


def map_http_error(status_code: int, message: str) -> None:
    """
    Maps HTTP status codes to domain-specific LLM errors.

    Rules:
    - 429 → rate limit (retryable)
    - 4xx → client error (non-retryable)
    - 5xx → server error (retryable)
    - others → retryable fallback
    """

    if status_code == 429:
        raise LLMRateLimitError(message)

    if status_code == 402:  # pagamento/quota
        raise LLMClientError(message, code="quota_exceeded")

    if 400 <= status_code < 500:
        raise LLMClientError(message)

    if 500 <= status_code < 600:
        raise LLMServerError(message)

    # ----------------------------------
    # DEFAULT (retryable)
    # ----------------------------------
    raise LLMRetryableError(f"[{status_code}] {message}")
