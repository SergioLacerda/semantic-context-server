import pytest

from semantic_context_server.application.services.intent.intent_classifier import (
    IntentClassifier,
)
from semantic_context_server.application.services.intent.language_profiles import (
    SUPPORTED_LANGUAGES,
)
from tests.config.fakes.infrastructure.llm.fake_llm import DummyLLM

# ---------------------------------------------------------
# SCORE BASE
# ---------------------------------------------------------


@pytest.mark.asyncio
async def test_empty_text_score():
    clf = IntentClassifier(SUPPORTED_LANGUAGES)

    score = await clf.score("")

    assert score < 0


@pytest.mark.asyncio
async def test_ooc_hard_reject():
    clf = IntentClassifier(SUPPORTED_LANGUAGES)

    score = await clf.score("(fala)")

    assert score <= -5


@pytest.mark.asyncio
async def test_weak_word_penalty():
    clf = IntentClassifier(SUPPORTED_LANGUAGES)

    score = await clf.score("ok")

    assert score < 0


@pytest.mark.asyncio
async def test_trigger_positive_score():
    clf = IntentClassifier(SUPPORTED_LANGUAGES)

    score = await clf.score("eu ataco o dragao")

    assert score > 2


# ---------------------------------------------------------
# LLM INFLUENCE
# ---------------------------------------------------------


@pytest.mark.asyncio
async def test_llm_score_applied():
    clf = IntentClassifier(SUPPORTED_LANGUAGES, DummyLLM("ACTION"))

    score = await clf.score("random text")

    assert score > 0


@pytest.mark.asyncio
async def test_llm_exception_fallback():
    clf = IntentClassifier(SUPPORTED_LANGUAGES, DummyLLM(fail=True))

    score = await clf.score("this is a long sentence")

    assert score >= 0


# ---------------------------------------------------------
# CLASSIFY (🔥 PRINCIPAL)
# ---------------------------------------------------------


@pytest.mark.asyncio
async def test_classify_action():
    clf = IntentClassifier(SUPPORTED_LANGUAGES)

    result = await clf.classify("eu ataco o goblin")

    assert result in ("ACTION", "EXPLORATION")


@pytest.mark.asyncio
async def test_classify_exploration():
    clf = IntentClassifier(SUPPORTED_LANGUAGES)

    result = await clf.classify("olho ao redor da sala")

    assert result in ("EXPLORATION", "ACTION")


@pytest.mark.asyncio
async def test_classify_chat():
    clf = IntentClassifier(SUPPORTED_LANGUAGES)

    result = await clf.classify("kkk isso foi engraçado")

    assert result in ("CHAT", "OOC")


@pytest.mark.asyncio
async def test_classify_ooc():
    clf = IntentClassifier(SUPPORTED_LANGUAGES)

    result = await clf.classify("(isso não faz sentido)")

    assert result in ("CHAT", "OOC")


# ---------------------------------------------------------
# IS_ACTION
# ---------------------------------------------------------


@pytest.mark.asyncio
async def test_is_action_true():
    clf = IntentClassifier(SUPPORTED_LANGUAGES)

    result = await clf.is_action("eu ataco o goblin")

    assert result is True


@pytest.mark.asyncio
async def test_is_action_false():
    clf = IntentClassifier(SUPPORTED_LANGUAGES)

    result = await clf.is_action("kkk isso foi engraçado")

    assert result is False


# ---------------------------------------------------------
# INTERNAL METHODS (comportamento, não valores fixos)
# ---------------------------------------------------------


def test_trigger_score_multiple():
    clf = IntentClassifier(SUPPORTED_LANGUAGES)

    triggers = list(SUPPORTED_LANGUAGES[0].triggers)

    if len(triggers) < 2:
        pytest.skip("Not enough triggers")

    text = f"{triggers[0]} {triggers[1]}"

    score = clf._trigger_score(text)

    assert score > 0


def test_trigger_score_none():
    clf = IntentClassifier(SUPPORTED_LANGUAGES)

    score = clf._trigger_score("hello world")

    assert score == 0


def test_length_score_progression():
    clf = IntentClassifier(SUPPORTED_LANGUAGES)

    short = clf._length_score("one two")
    medium = clf._length_score("one two three four")
    long = clf._length_score("one two three four five six seven eight")

    assert short <= medium <= long


def test_llm_score_signs():
    clf = IntentClassifier(SUPPORTED_LANGUAGES)

    assert clf._llm_score("ACTION") > 0
    assert clf._llm_score("CHAT") < 0
    assert clf._llm_score("OOC") < 0
    assert clf._llm_score("UNKNOWN") == 0


def test_is_ooc_detection():
    clf = IntentClassifier(SUPPORTED_LANGUAGES)

    assert clf._is_ooc("(fala)") is True
    assert clf._is_ooc("isso está bugado") is True
    assert clf._is_ooc("ataco o goblin") is False


def test_is_too_short():
    clf = IntentClassifier(SUPPORTED_LANGUAGES)

    assert clf._is_too_short("hi") is True
    assert clf._is_too_short("hello world") is False
