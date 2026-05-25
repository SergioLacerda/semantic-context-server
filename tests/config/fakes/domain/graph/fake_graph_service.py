class FakeNarrativeGraphService:
    """
    Fake de NarrativeGraphService

    ✔ async compatível
    ✔ captura chamadas
    ✔ comportamento configurável
    ✔ usado em cenários / integração
    """

    def __init__(self):
        self.updated_events = []
        self.related_queries = []

        self._related_result = set()

    # ---------------------------------------------------------
    # UPDATE
    # ---------------------------------------------------------

    async def update_from_event(self, text: str):
        self.updated_events.append(text)

    # ---------------------------------------------------------
    # QUERY
    # ---------------------------------------------------------

    async def related(self, query: str) -> set:
        self.related_queries.append(query)
        return set(self._related_result)

    # ---------------------------------------------------------
    # CONFIG
    # ---------------------------------------------------------

    def set_related_result(self, values):
        self._related_result = set(values)

    # ---------------------------------------------------------
    # HELPERS
    # ---------------------------------------------------------

    def last_event(self):
        return self.updated_events[-1] if self.updated_events else None

    def last_query(self):
        return self.related_queries[-1] if self.related_queries else None
