import re


class SimpleTokenizer:
    def tokenize(self, text: str) -> list[str]:
        return re.findall(r"\w+", text.lower())
