from collections import defaultdict
from types import SimpleNamespace


class FakeMemoryService:
    """
    Fake robusto para testes de ContextBuilder e Narrative.

    ✔ multi-campaign
    ✔ suporta history (recent)
    ✔ suporta memória RAG (vector/semantic)
    ✔ determinístico para golden tests
    ✔ compatível com arquitetura real
    """

    def __init__(self, history=None, vector=None):
        self._history = defaultdict(list)
        self._vector = defaultdict(list)

        if history:
            self._history["default"] = list(history)

        if vector:
            self._vector["default"] = list(vector)

    # ==========================================================
    # LOAD MEMORY
    # ==========================================================

    async def load_memory(self, campaign_id):
        history = self._history.get(campaign_id, [])

        return SimpleNamespace(
            summary="",
            recent_events=history,
        )

    # ==========================================================
    # CONTEXT (RAG)
    # ==========================================================

    async def get_context(self, campaign_id: str, query: str):
        history = self._history.get(campaign_id, [])
        vector = self._vector.get(campaign_id, [])

        return {
            "summary": "",
            "recent": history,
            "semantic": vector,
            "vector": vector,
            "graph": [],
        }

    # ==========================================================
    # WRITE
    # ==========================================================

    async def append(self, campaign_id, text):
        self._history[campaign_id].append(text)

    # ==========================================================
    # CLEAR
    # ==========================================================

    async def clear(self, campaign_id):
        self._history[campaign_id] = []
        self._vector[campaign_id] = []

    # ==========================================================
    # TEST HELPERS
    # ==========================================================

    def set_history(self, campaign_id: str, history: list[str]):
        self._history[campaign_id] = list(history)

    def set_vector(self, campaign_id: str, docs: list[str]):
        self._vector[campaign_id] = list(docs)
