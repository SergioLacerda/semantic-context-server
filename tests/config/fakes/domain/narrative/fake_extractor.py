class FakeExtractor:
    def __init__(self, entities):
        self.entities = entities
        self.called_with = None

    def extract(self, text):
        self.called_with = text
        return self.entities
