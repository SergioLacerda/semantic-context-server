import logging
from collections.abc import Iterable
from typing import Any, cast

logger = logging.getLogger("semantic_context_server.ann.ivf")


class IVFRouter:
    """
    Implementação simples de ANN baseada em clusters (IVF-like).
    """

    def __init__(self) -> None:
        self._index: Any = None

    def set_index(self, index: Any) -> None:
        """
        index deve expor:
        - search(query_vector, k)
        """
        self._index = index

    # 🔥 agora segue contrato ANN
    async def search(self, query_vector: list[float], k: int = 10) -> list[str]:
        if not self._index:
            return []

        try:
            return cast(list[str], await self._index.search(query_vector, k))

        except Exception:
            logger.exception("IVF search failed")
            return []

    # ⚠️ opcional (legado)
    async def route(self, query_vector: list[float]) -> Iterable[str]:
        if self._index is not None and hasattr(self._index, "route"):
            return cast(Iterable[str], await self._index.route(query_vector))
        return []
