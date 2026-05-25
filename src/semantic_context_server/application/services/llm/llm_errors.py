class LLMError(Exception):
    """
    Base error for LLM layer.
    All LLM-related exceptions should inherit from this.
    """


# ---------------------------------------------------------
# CLIENT ERRORS (não retry)
# ---------------------------------------------------------


class LLMClientError(LLMError):
    def __init__(self, message: str, *, code: str | None = None):
        super().__init__(message)
        self.code = code  # ex: "insufficient_quota"


# ---------------------------------------------------------
# RETRYABLE ERRORS
# ---------------------------------------------------------


class LLMRetryableError(LLMError):
    """
    Base class for retryable errors.
    """


class LLMTimeoutError(LLMRetryableError):
    """
    Timeout controlado pelo serviço (asyncio / rede).
    """


class LLMRateLimitError(LLMRetryableError):
    """
    Rate limit (429).
    Retry recomendado com backoff.
    """


class LLMServerError(LLMRetryableError):
    """
    Erros 5xx.
    """


class LLMNetworkError(LLMRetryableError):
    """
    Falhas de rede (connection reset, DNS, etc).
    """
