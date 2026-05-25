from typing import Any


class LLMIntentClassifier:
    def __init__(self, llm_factory: Any) -> None:
        self._llm_factory = llm_factory
        self._llm: Any = None

    # ---------------------------------------------------------

    def _get_llm(self) -> Any:
        if self._llm is None:
            self._llm = self._llm_factory()
        return self._llm

    # ---------------------------------------------------------
    # 🔥 heurística leve (rápida e barata)
    # ---------------------------------------------------------

    def _rule_based(self, text: str) -> str | None:
        t = text.lower()

        # ação típica de RPG
        if any(w in t for w in ["ataco", "olho", "corro", "entro", "pego", "investigo"]):
            return "ACTION"

        # chat casual
        if any(w in t for w in ["oi", "ola", "kk", "haha", "fala", "mano"]):
            return "CHAT"

        return None

    # ---------------------------------------------------------

    async def classify(self, text: str, campaign_id: str) -> str:
        rule = self._rule_based(text)
        if rule:
            return rule

        llm = self._get_llm()

        request = {
            "prompt": text,
            "campaign_id": campaign_id,
            "temperature": 0.0,
            "max_tokens": 5,
            "system_prompt": "...",
        }

        try:
            response = await llm.generate(request)

            if not response:
                return "CHAT"

            raw = response.content if hasattr(response, "content") else response
            return self._normalize_result(raw)

        except Exception:
            return "CHAT"

    def _normalize_result(self, value: Any) -> str:
        result = str(value).strip().upper().replace("\n", " ")

        if result in ("ACTION", "CHAT", "OOC"):
            return result
        if "ACTION" in result:
            return "ACTION"
        if "OOC" in result:
            return "OOC"
        if "CHAT" in result:
            return "CHAT"
        return "CHAT"
