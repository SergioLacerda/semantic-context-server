class FakeIntentClassifier:
    def __init__(
        self,
        llm_classifier=None,
        threshold: float = 2.0,
    ):
        self.fixed_intent: str | None = None
        if isinstance(llm_classifier, str):
            self.fixed_intent = llm_classifier
            llm_classifier = None

        self.llm = llm_classifier
        self.threshold = threshold

        self.calls: list[str] = []

    # ---------------------------------------------------------
    # PUBLIC
    # ---------------------------------------------------------

    async def classify(self, text: str) -> str:
        self.calls.append(text)

        if self.fixed_intent:
            return self.fixed_intent

        if not text:
            return "CHAT"

        t = text.lower()

        # ------------------------------------------------------
        # LLM override (se fornecido)
        # ------------------------------------------------------
        if self.llm:
            try:
                return await self.llm.classify(text)
            except Exception:
                pass

        # ------------------------------------------------------
        # heurística determinística
        # ------------------------------------------------------

        if any(w in t for w in ["attack", "ataco", "open", "pego", "entro"]):
            return "ACTION"

        if any(w in t for w in ["look", "olho", "inspect", "investigo"]):
            return "EXPLORATION"

        if any(w in t for w in ["bug", "erro", "wtf", "isso nao", "isso não"]):
            return "OOC"

        return "CHAT"

    async def score(self, text: str) -> float:
        classification = await self.classify(text)

        mapping = {
            "ACTION": 3.0,
            "EXPLORATION": 2.0,
            "CHAT": 0.0,
            "OOC": -5.0,
        }

        return mapping.get(classification, 0.0)

    async def is_action(self, text: str) -> bool:
        return (await self.score(text)) >= self.threshold
