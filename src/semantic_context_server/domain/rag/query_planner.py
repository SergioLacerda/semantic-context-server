class QueryPlanner:
    ROLL_KEYWORDS = {"roll", "dado", "d20", "d6", "rolar"}

    def classify_intent(self, q: str) -> str:
        q = q.lower()

        if any(k in q for k in self.ROLL_KEYWORDS):
            return "roll"

        return "narrative"
