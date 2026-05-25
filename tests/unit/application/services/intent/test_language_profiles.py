from semantic_context_server.application.services.intent.language_profiles import (
    EN,
    PT_BR,
    SUPPORTED_LANGUAGES,
)


def test_profiles_loaded():
    assert PT_BR is not None
    assert EN is not None
    assert len(SUPPORTED_LANGUAGES) == 2


def test_pt_br_triggers():
    assert "ataco" in PT_BR.triggers
    assert "kkk" in PT_BR.weak_words


def test_en_triggers():
    assert "attack" in EN.triggers
    assert "lol" in EN.weak_words
