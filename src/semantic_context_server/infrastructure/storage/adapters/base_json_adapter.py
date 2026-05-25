import json
import logging
import os
import tempfile
import threading
from pathlib import Path
from typing import Any, TypeVar

from semantic_context_server.application.ports.executor import ExecutorPort
from semantic_context_server.infrastructure.serialization.json_serializer import JSONSerializer
from semantic_context_server.shared.text_io import read_text_utf8

logger = logging.getLogger(__name__)

T = TypeVar("T")


class BaseJsonAdapter:
    """
    Base para adaptadores JSON seguindo ia-rules.md:
    ✔ 100% Async Port (via Executor)
    ✔ Atomic Writes (os.replace)
    ✔ Thread-Safe (threading.Lock)
    """

    _file_locks: dict[Path, threading.Lock] = {}
    _global_lock = threading.Lock()

    def __init__(self, file_path: Path, executor: ExecutorPort, serializer: JSONSerializer):
        self.path = file_path
        self.executor = executor
        self.serializer = serializer

        # Garantir um lock único por caminho de arquivo
        with self._global_lock:
            if self.path not in self._file_locks:
                self._file_locks[self.path] = threading.Lock()
            self.lock = self._file_locks[self.path]

    async def _read_file(self) -> Any:
        return await self.executor.run(self._read_sync)

    async def _write_file(self, data: Any) -> None:
        await self.executor.run(self._write_sync, data)

    def _read_sync(self) -> Any:
        with self.lock:
            if not self.path.exists():
                return None
            return json.loads(read_text_utf8(self.path))

    def _write_sync(self, data: Any) -> None:
        with self.lock:
            self.path.parent.mkdir(parents=True, exist_ok=True)

            # Higieniza os dados usando o serializer padrão do projeto
            sanitized_data = self.serializer.serialize(data)

            # Escrita Atômica
            fd, temp_path = tempfile.mkstemp(dir=self.path.parent, suffix=".tmp")
            try:
                with os.fdopen(fd, "w", encoding="utf-8") as f:
                    json.dump(sanitized_data, f, indent=2, ensure_ascii=False)
                os.replace(temp_path, self.path)
            except Exception as e:
                logger.error(f"Failed atomic write to {self.path}: {str(e)}")
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                raise
