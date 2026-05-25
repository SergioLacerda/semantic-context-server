from typing import Any


class BaseHarness:
    """
    Base para harness de testes.

    ✔ separa chamadas (calls) de eventos (events)
    ✔ fornece helpers de inspeção
    ✔ pronto para evolução (trace/debug)
    """

    def __init__(self):
        self.calls: list[dict[str, Any]] = []
        self.events: list[dict[str, Any]] = []

    # ---------------------------------------------------------
    # RECORDING
    # ---------------------------------------------------------

    def record_call(self, **data) -> None:
        """Registra uma ação relevante do cenário"""
        self.calls.append(data)

    def record_event(self, **data) -> None:
        """Registra evento interno (infra/debug)"""
        self.events.append(data)

    def record(self, *args, **kwargs):
        raise NotImplementedError("Use record_event instead")

    # ---------------------------------------------------------
    # ACCESSORS
    # ---------------------------------------------------------

    def last_call(self) -> dict[str, Any] | None:
        return self.calls[-1] if self.calls else None

    def call_count(self) -> int:
        return len(self.calls)

    def event_count(self) -> int:
        return len(self.events)

    # ---------------------------------------------------------
    # FILTERS (🔥 MUITO ÚTIL)
    # ---------------------------------------------------------

    def calls_by(self, **filters) -> list[dict[str, Any]]:
        return [c for c in self.calls if all(c.get(k) == v for k, v in filters.items())]

    def events_by(self, **filters) -> list[dict[str, Any]]:
        return [e for e in self.events if all(e.get(k) == v for k, v in filters.items())]

    # ---------------------------------------------------------
    # RESET
    # ---------------------------------------------------------

    def reset(self) -> None:
        self.calls.clear()
        self.events.clear()

    # ---------------------------------------------------------
    # DEBUG
    # ---------------------------------------------------------

    def dump_calls(self) -> None:
        print("\n=== CALLS ===")
        for i, call in enumerate(self.calls):
            print(f"[{i}] {call}")

    def dump_events(self) -> None:
        print("\n=== EVENTS ===")
        for i, event in enumerate(self.events):
            print(f"[{i}] {event}")
