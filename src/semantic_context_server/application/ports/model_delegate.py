from abc import ABC, abstractmethod
from typing import Any


class ModelDelegatePort(ABC):
    @abstractmethod
    async def run(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Execute the model (external API or local) and return a dict with at least ``prompt``."""
        ...
