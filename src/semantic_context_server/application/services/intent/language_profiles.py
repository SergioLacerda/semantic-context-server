class LanguageProfile:
    def __init__(self, weak_words: set[str], triggers: list[str]) -> None:
        self.weak_words = weak_words
        self.triggers = triggers


PT_BR = LanguageProfile(
    weak_words={"kkk", "ok", "sim", "não", "haha", "ata", "hm"},
    triggers=[
        "ataco",
        "entro",
        "uso",
        "vou",
        "olho",
        "faço",
        "corro",
        "lanço",
        "subo",
        "desço",
        "pego",
        "abro",
        "fecho",
    ],
)


EN = LanguageProfile(
    weak_words={"ok", "yes", "no", "lol", "haha", "hmm"},
    triggers=[
        "attack",
        "enter",
        "use",
        "go",
        "look",
        "do",
        "run",
        "throw",
        "climb",
        "descend",
        "grab",
        "open",
        "close",
    ],
)


SUPPORTED_LANGUAGES = [PT_BR, EN]
