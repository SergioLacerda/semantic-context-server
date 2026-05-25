from typing import Any


class KeywordQueryClassifier:
    def __init__(self, tokenizer: Any, vocabulary: Any) -> None:
        self.tokenizer = tokenizer
        self.vocabulary = vocabulary

    def classify(self, query: str) -> str:
        tokens = self.tokenizer.tokenize(query)

        scores = {k: 0 for k in self.vocabulary}

        for token in tokens:
            for category, vocab in self.vocabulary.items():
                if token in vocab:
                    scores[category] += 1

        best = max(scores, key=lambda k: scores[k])

        if scores[best] == 0:
            return "exploration"

        return str(best)
