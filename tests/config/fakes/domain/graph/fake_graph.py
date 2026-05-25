class FakeGraph:
    def __init__(self):
        self.updated_text = None
        self.updated_entities = None
        self.updated_context = None

        self.related_query = None
        self._related_result = set()

    # ---------------------------------------------------------
    # UPDATE
    # ---------------------------------------------------------
    def update(self, entities, context=None, text=None):
        self.updated_entities = entities
        self.updated_context = context
        self.updated_text = text

    # ---------------------------------------------------------
    # RELATED
    # ---------------------------------------------------------
    def related(self, entities):
        self.related_query = " ".join(entities) if isinstance(entities, list) else entities
        return set(self._related_result)

    # ---------------------------------------------------------
    # CONFIG
    # ---------------------------------------------------------
    def set_related_result(self, values):
        self._related_result = set(values)
