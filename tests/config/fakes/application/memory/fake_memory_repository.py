class FakeMemoryRepository:
    def __init__(self, initial=None):
        self._store = initial or {}
        self.calls = []

    async def load(self, campaign_id: str):
        self.calls.append(("load", campaign_id))

        data = self._store.get(campaign_id)

        return self._normalize(data)

    async def save(self, campaign_id: str, data):
        self.calls.append(("save", campaign_id, data))

        # 🔥 SEMPRE salvar normalizado
        self._store[campaign_id] = self._normalize(data)

    def get_memory(self, campaign_id: str):
        # 🔥 CRÍTICO: normalizar também aqui
        return self._normalize(self._store.get(campaign_id))

    # ==========================================================
    # INTERNAL
    # ==========================================================

    def _normalize(self, data):
        """
        🔥 Garante formato correto SEMPRE
        """

        if not data:
            return {
                "recent_events": [],
                "world_facts": [],
                "scene_state": [],
                "summary": "",
            }

        # 🔥 caso legado / erro → lista
        if isinstance(data, list):
            return {
                "recent_events": data,
                "world_facts": [],
                "scene_state": [],
                "summary": "",
            }

        # 🔥 caso dict válido
        if isinstance(data, dict):
            return {
                "recent_events": data.get("recent_events", []),
                "world_facts": data.get("world_facts", []),
                "scene_state": data.get("scene_state", []),
                "summary": data.get("summary", ""),
            }

        # fallback defensivo
        return {
            "recent_events": [],
            "world_facts": [],
            "scene_state": [],
            "summary": "",
        }
