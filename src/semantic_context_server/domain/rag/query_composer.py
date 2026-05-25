class QueryComposer:
    """
    Responsável por compor a query para o Retrieval (RAG).
    """

    def __init__(self, *, max_summary_chars: int = 200):
        self.max_summary_chars = max_summary_chars

    def build(
        self,
        *,
        action: str,
        summary: str = "",
        recent_events: list[str] | None = None,
    ) -> str:
        recent_events = recent_events or []

        # 🔥 memória recente (curto prazo)
        memory_hint = " ".join(recent_events[-3:])

        # 🔥 resumo (longo prazo - truncado)
        summary_hint = summary[: self.max_summary_chars].strip()

        parts = [
            action.strip(),
            memory_hint,
            summary_hint,
        ]

        return " ".join(p for p in parts if p).strip()
