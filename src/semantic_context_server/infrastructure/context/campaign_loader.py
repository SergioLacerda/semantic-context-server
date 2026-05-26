import logging
from pathlib import Path
from typing import Any

from packages.core.shared_kernel.execution import on_executor
from packages.core.shared_kernel.text_io import read_text_utf8

logger = logging.getLogger(__name__)


class CampaignLoader:
    def __init__(self, base_dir: Path, executor: Any = None) -> None:
        self.base_dir = base_dir
        self.executor = executor

    async def load_documents(self) -> list[str]:
        """
        Carrega documentos da campanha de forma não bloqueante.
        Utiliza o Executor para offload de I/O de disco.
        """
        result: list[str] = await self._load_sync()
        return result

    @on_executor
    def _load_sync(self) -> list[str]:
        """Lógica síncrona de leitura para ser executada no pool de threads."""
        texts = []

        if not self.base_dir.exists():
            logger.warning("Campaign directory not found: %s", self.base_dir)
            return []

        try:
            for file in self.base_dir.rglob("*.md"):
                try:
                    texts.append(read_text_utf8(file, errors="strict"))
                except Exception as e:
                    logger.warning("Failed to read campaign file %s: %s", file, e)
        except Exception as e:
            logger.error("Error scanning campaign directory %s: %s", self.base_dir, e)

        return texts
