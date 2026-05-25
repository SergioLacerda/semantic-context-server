# src/semantic_context_server/shared/logging/config.py

import logging

from semantic_context_server.config.loader import load_settings


def setup_logging() -> None:
    # 1. Obtém as configurações centralizadas (SettingsLoader já validou o ambiente)
    settings = load_settings()

    logging.basicConfig(
        level=settings.runtime.log_level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )

    # 2. Reduzir ruído de bibliotecas de infraestrutura
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("discord").setLevel(logging.WARNING)
