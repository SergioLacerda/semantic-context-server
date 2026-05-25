import pytest

from semantic_context_server.application.services.context_selector import ContextSelector


class FakeTokenizer:
    def tokenize(self, text):
        return text.split()


@pytest.fixture
def tokenizer():
    return FakeTokenizer()


@pytest.fixture
def selector():
    def _build(max_tokens=2000):
        return ContextSelector(max_tokens=max_tokens)

    return _build


def test_select_within_token_limit(selector, tokenizer):
    s = selector(10)

    docs = ["um dois", "tres quatro", "cinco"]

    result = s.select(docs, tokenizer)

    assert result == docs


def test_select_respects_max_tokens(selector, tokenizer):
    s = selector(3)

    docs = ["um dois", "tres quatro", "cinco"]

    result = s.select(docs, tokenizer)

    assert result == ["um dois"]


def test_select_stops_on_overflow(selector, tokenizer):
    s = selector(3)

    docs = ["um dois", "tres quatro", "cinco seis sete"]

    result = s.select(docs, tokenizer)

    assert result == ["um dois"]


def test_select_preserves_order(selector, tokenizer):
    s = selector(5)

    docs = ["a", "bb", "ccc"]

    result = s.select(docs, tokenizer)

    assert result == docs


def test_first_doc_exceeds_limit(selector, tokenizer):
    s = selector(1)

    docs = ["um dois"]

    result = s.select(docs, tokenizer)

    assert result == []


def test_extract_text_from_string():
    s = ContextSelector()

    assert s._extract_text("abc") == "abc"


def test_extract_text_from_dict():
    s = ContextSelector()

    assert s._extract_text({"text": "conteudo"}) == "conteudo"


def test_extract_text_dict_without_text():
    s = ContextSelector()

    assert s._extract_text({"foo": "bar"}) == ""


def test_extract_text_fallback():
    s = ContextSelector()

    class Obj:
        def __str__(self):
            return "custom"

    assert s._extract_text(Obj()) == "custom"
