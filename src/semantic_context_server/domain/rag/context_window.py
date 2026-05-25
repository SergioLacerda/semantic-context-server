import re
from typing import Any


class DynamicContextWindow:
    """
    Responsável por ajustar dinamicamente a quantidade de contexto
    com base no tipo de cena.
    """

    def __init__(self) -> None:
        # ---------------------------------------------------------
        # políticas por tipo de cena
        # ---------------------------------------------------------

        self.policies = {
            "combat": {
                "max_docs": 4,
                "max_history": 3,
            },
            "dialogue": {
                "max_docs": 6,
                "max_history": 8,
            },
            "investigation": {
                "max_docs": 8,
                "max_history": 5,
            },
            "exploration": {
                "max_docs": 6,
                "max_history": 5,
            },
        }

        # ---------------------------------------------------------
        # vocabulário para classificação leve
        # ---------------------------------------------------------

        self.vocabulary = {
            "combat": {
                "atacar",
                "ataque",
                "golpe",
                "lutar",
                "attack",
                "fight",
                "strike",
                "combat",
            },
            "dialogue": {"pergunto", "falo", "digo", "ask", "tell", "say", "talk"},
            "investigation": {
                "investigo",
                "procuro",
                "pista",
                "investigate",
                "search",
                "clue",
            },
            "exploration": {"exploro", "entro", "vasculho", "explore", "enter", "look"},
        }

    # ---------------------------------------------------------
    # classificação
    # ---------------------------------------------------------

    def tokenize(self, text: str) -> list[str]:
        return re.findall(r"\w+", text.lower())

    def classify(self, query: str) -> str:
        tokens = self.tokenize(query)

        scores = {k: 0 for k in self.vocabulary}

        for token in tokens:
            for category, vocab in self.vocabulary.items():
                if token in vocab:
                    scores[category] += 1

        best = max(scores, key=lambda k: scores[k])
        if scores[best] == 0:
            return "exploration"

        return best

    # ---------------------------------------------------------
    # política dinâmica
    # ---------------------------------------------------------

    def get_policy(self, action: str) -> dict:
        scene_type = self.classify(action)

        base = self.policies.get(scene_type, self.policies["exploration"])

        # ajuste leve por tamanho da ação
        if len(action) < 40:
            base = base.copy()
            base["max_docs"] = max(3, base["max_docs"] - 2)

        return base

    # ---------------------------------------------------------
    # aplicação da política
    # ---------------------------------------------------------

    def apply(self, docs: list[Any], policy: Any) -> list[Any]:
        if not docs:
            return []

        max_docs = policy.get("max_docs", 5)

        return docs[:max_docs]
