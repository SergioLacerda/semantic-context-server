import re


class EntityExtractor:
    """
    Extrator simples de entidades (placeholder).
    Pode ser substituído por spaCy, LLM, etc.
    """

    def __init__(self, min_length: int = 3):
        self.min_length = min_length

    def extract(self, text: str) -> list[str]:
        tokens = re.findall(r"\w+", text)

        return [t.lower() for t in tokens if len(t) >= self.min_length]
