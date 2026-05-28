from __future__ import annotations

import contextvars
import logging

from packages.core.runtime_config.loader import load_settings

request_id_var: contextvars.ContextVar[str] = contextvars.ContextVar("request_id", default="-")


def set_request_id(request_id: str) -> None:
    request_id_var.set(request_id)


def get_request_id() -> str:
    return request_id_var.get()


def setup_logging() -> None:
    settings = load_settings()
    logging.basicConfig(
        level=settings.runtime.log_level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("discord").setLevel(logging.WARNING)
