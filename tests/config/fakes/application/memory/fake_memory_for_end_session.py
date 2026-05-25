from types import SimpleNamespace


class FakeEndSessionMemory:
    def __init__(self, events=None):
        self.events = list(events or [])
        self.cleared = False
        self.calls: list[dict] = []

    # ---------------------------------------------------------
    # LOAD
    # ---------------------------------------------------------

    async def load_memory(self, campaign_id):
        self.calls.append({"op": "load_memory", "campaign_id": campaign_id})

        return SimpleNamespace(
            recent_events=self.events,
            summary="",
        )

    # ---------------------------------------------------------
    # CLEAR
    # ---------------------------------------------------------

    async def clear(self, campaign_id):
        self.calls.append({"op": "clear", "campaign_id": campaign_id})

        self.cleared = True
        self.events.clear()
