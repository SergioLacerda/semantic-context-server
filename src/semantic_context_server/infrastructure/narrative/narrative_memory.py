from typing import Any


class NarrativeMemory:
    """
    Representa a memória narrativa de uma campanha.

    ✔ Armazena eventos recentes (episódicos)
    ✔ Compatível com MemoryService
    ✔ Pronta para summarization / compressão
    ✔ Independente de infraestrutura
    """

    def __init__(self, events: list[str] | None = None):
        self._events: list[str] = events or []

    # ==========================================================
    # PROPERTIES
    # ==========================================================

    @property
    def recent_events(self) -> list[str]:
        return list(self._events)

    # ==========================================================
    # CORE OPERATIONS
    # ==========================================================

    def add_event(self, text: str) -> None:
        if not text:
            return

        cleaned = str(text).strip()
        if not cleaned:
            return

        self._events.append(cleaned)

    def extend(self, events: list[str]) -> None:
        for e in events:
            self.add_event(e)

    def clear(self) -> None:
        self._events.clear()

    # ==========================================================
    # OVERFLOW / LIMIT
    # ==========================================================

    def trim(self, max_events: int) -> None:
        """
        Mantém apenas os últimos N eventos.
        """
        if max_events <= 0:
            self._events = []
            return

        if len(self._events) > max_events:
            self._events = self._events[-max_events:]

    # ==========================================================
    # SERIALIZATION
    # ==========================================================

    def to_dict(self) -> list[dict[str, Any]]:
        """
        Formato esperado pelo repository:
        [
            {"text": "..."},
            ...
        ]
        """
        return [{"text": e} for e in self._events]

    @classmethod
    def from_dict(cls, data: list[dict[str, Any]] | None) -> "NarrativeMemory":
        if not data:
            return cls([])

        events = []

        for item in data:
            if isinstance(item, dict):
                events.append(str(item.get("text", "") or ""))
            else:
                events.append(str(item))

        return cls(events)

    # ==========================================================
    # DEBUG / UTILS
    # ==========================================================

    def __len__(self) -> int:
        return len(self._events)

    def __repr__(self) -> str:
        return f"NarrativeMemory(events={len(self._events)})"
