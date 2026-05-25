class FakeLLMIntentClassifier:
    def __init__(self, mapping: dict[str, str] | None = None):
        """
        mapping:
            {"attack": "ACTION", "hello": "CHAT"}
        """
        self.mapping = mapping or {}
        self.calls: list[dict] = []

    async def classify(self, text: str, campaign_id: str | None = None) -> str:
        self.calls.append(
            {
                "text": text,
                "campaign_id": campaign_id,
            }
        )

        if not text:
            return "CHAT"

        t = text.lower()

        # mapping explícito (prioridade máxima)
        for key, value in self.mapping.items():
            if key in t:
                return value

        # heurística simples (alinhada com real)
        if any(w in t for w in ["attack", "ataco", "hit", "open", "pego", "entro"]):
            return "ACTION"

        if any(w in t for w in ["oi", "ola", "hello", "kk", "haha"]):
            return "CHAT"

        if any(w in t for w in ["bug", "erro", "wtf"]):
            return "OOC"

        return "CHAT"
