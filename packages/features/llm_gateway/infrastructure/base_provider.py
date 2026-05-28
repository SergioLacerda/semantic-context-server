import time
from abc import ABC, abstractmethod
from typing import Any

from packages.features.llm_gateway.dto import LLMRequest
from packages.features.llm_gateway.dto import LLMResponse
from packages.features.llm_gateway.application.error_mapper import map_http_error
from packages.features.llm_gateway.application.llm_errors import (
    LLMClientError,
    LLMRetryableError,
)


class BaseProvider(ABC):
    """
    Base para todos providers LLM.

    Responsável por:
    - timeout
    - logging
    - error handling
    - validação de resposta
    """

    def __init__(self, provider_name: str, model: str, timeout: float | None = None):
        self.provider_name = provider_name
        self.model = model
        self.timeout = timeout

    # ---------------------------------------------------------
    # ENTRYPOINT
    # ---------------------------------------------------------

    async def generate(self, request: LLMRequest) -> LLMResponse:
        return await self.generate_from_request(request)

    # ---------------------------------------------------------

    async def generate_from_request(self, request: LLMRequest) -> LLMResponse:
        start = time.perf_counter()

        try:
            resp = await self._call_api(request)

            # -------------------------------------------------
            # EXTRAÇÃO + NORMALIZAÇÃO
            # -------------------------------------------------
            content = self._extract_content(resp)

            if content is None:
                content = ""

            if not isinstance(content, str):
                content = str(content)

            # -------------------------------------------------
            # VALIDAÇÃO ROBUSTA
            # -------------------------------------------------
            if not content.strip():
                raise LLMRetryableError("Empty response")

            # -------------------------------------------------
            # MÉTRICAS
            # -------------------------------------------------
            latency = (time.perf_counter() - start) * 1000

            usage = self._extract_usage(resp) or {}

            # -------------------------------------------------
            # RESPONSE PADRONIZADO
            # -------------------------------------------------
            return LLMResponse(
                content=content,
                provider=self.provider_name,
                model=self.model,
                latency_ms=latency,
                **usage,
            )

        # ---------------------------------------------------------
        # ERROS
        # ---------------------------------------------------------

        except TimeoutError as e:
            raise ValueError("timeout") from e

        except ValueError as e:
            raise LLMClientError(str(e)) from e

        except LLMRetryableError:
            raise

        except Exception as e:
            status = getattr(e, "status_code", None)
            if status:
                map_http_error(status, str(e))

            raise LLMRetryableError(str(e)) from e

    # ---------------------------------------------------------
    # EXTENSÃO (cada provider implementa)
    # ---------------------------------------------------------

    @abstractmethod
    async def _call_api(self, request: LLMRequest) -> Any:
        pass

    @abstractmethod
    def _extract_content(self, resp: Any) -> str:
        pass

    # ---------------------------------------------------------
    # OPCIONAIS
    # ---------------------------------------------------------

    def _extract_usage(self, resp: Any) -> dict[str, Any]:
        return {}
