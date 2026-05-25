import pytest

from semantic_context_server.application.services.intent.intent_classifier import IntentClassifier
from tests.config.fakes.infrastructure.llm.fake_llm import DummyLLM


class Profile:
    def __init__(self):
        self.triggers = ["attack", "run"]
        self.weak_words = ["maybe"]


@pytest.mark.asyncio
async def test_empty_text_score():
    clf = IntentClassifier([Profile()])

    score = await clf.score("   ")

    assert score == -10.0


@pytest.mark.asyncio
async def test_llm_exception_ignored():
    clf = IntentClassifier([Profile()], llm_classifier=DummyLLM(fail=True))

    score = await clf.score("attack now")

    assert isinstance(score, float)


@pytest.mark.asyncio
async def test_weak_penalty_no_match():
    clf = IntentClassifier([Profile()])

    score = await clf.score("attack enemy")

    assert score > 0


def test_llm_score_unknown():
    clf = IntentClassifier([Profile()])

    score = clf._llm_score("SOMETHING_ELSE")

    assert score == 0.0


def test_llm_score_empty():
    clf = IntentClassifier([Profile()])

    assert clf._llm_score("") == 0.0


@pytest.mark.asyncio
async def test_classify_paths():
    clf = IntentClassifier([Profile()])

    assert await clf.classify("attack run enemy now quickly") == "ACTION"

    assert await clf.classify("attack enemy now") == "EXPLORATION"

    assert await clf.classify("isso está bugado") == "OOC"

    assert await clf.classify("hello") == "CHAT"
