import pytest

from semantic_context_server.application.services.intent.intent_classifier import (
    IntentClassifier,
)
from semantic_context_server.application.services.intent.language_profiles import (
    SUPPORTED_LANGUAGES,
)

# ---------------------------------------------------------
# MATCH INTELIGENTE
# ---------------------------------------------------------


def match_intent(result: str, expected: str) -> bool:
    if expected == "ACTION":
        return result in ("ACTION", "EXPLORATION")

    if expected == "EXPLORATION":
        return result in ("EXPLORATION", "ACTION")

    if expected == "CHAT":
        return result in ("CHAT", "OOC")

    return result == expected


# ---------------------------------------------------------
# EXPANDER
# ---------------------------------------------------------


class IntentDatasetExpander:
    def expand(self, text: str, n: int = 3):
        variants = set()

        for _ in range(n):
            variants.add(text)
            variants.add(f"{text} agora")
            variants.add(f"{text} rapidamente")

        return list(variants)


# ---------------------------------------------------------
# DATASET BASE
# ---------------------------------------------------------

DATASET_INTENT = [
    ("eu ataco o goblin", "ACTION"),
    ("saco minha espada", "ACTION"),
    ("olho ao redor", "EXPLORATION"),
    ("kkk isso foi engraçado", "CHAT"),
    ("isso está bugado", "OOC"),
]


# ---------------------------------------------------------
# TESTE PRINCIPAL
# ---------------------------------------------------------


async def _run_base_pass(clf, expander) -> tuple[list, list]:
    errors = []
    expanded_tests = []
    for text, expected in DATASET_INTENT:
        result = await clf.classify(text)
        expanded_tests.extend((v, expected) for v in expander.expand(text, n=3))
        if not match_intent(result, expected):
            errors.append((text, expected, result))
            expanded_tests.extend((v, expected) for v in expander.expand(text, n=5))
    return errors, expanded_tests


async def _run_expansion_pass(clf, expanded_tests: list) -> list:
    errors = []
    for text, expected in expanded_tests:
        result = await clf.classify(text)
        if not match_intent(result, expected):
            errors.append((text, expected, result))
    return errors


def _print_errors(label: str, errors: list) -> None:
    if errors:
        print(f"\n--- {label} ---")
        for t, e, r in errors:
            print(f"[{e}] {t} → {r}")


@pytest.mark.asyncio
async def test_intent_dataset_with_expansion():
    clf = IntentClassifier(SUPPORTED_LANGUAGES)
    expander = IntentDatasetExpander()

    errors, expanded_tests = await _run_base_pass(clf, expander)
    expansion_errors = await _run_expansion_pass(clf, expanded_tests)

    base_accuracy = 1 - (len(errors) / len(DATASET_INTENT))
    expansion_accuracy = (
        1 - (len(expansion_errors) / len(expanded_tests)) if expanded_tests else 1.0
    )

    _print_errors("BASE ERRORS", errors)
    _print_errors("EXPANSION ERRORS", expansion_errors)

    assert base_accuracy >= 0.75
    assert expansion_accuracy >= 0.30
