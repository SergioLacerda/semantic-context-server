from semantic_context_server.infrastructure.nlp.entity_extractor import (
    EntityExtractor,
)


def test_extract_basic():
    extractor = EntityExtractor()

    result = extractor.extract("Dragon attacks village")

    assert result == ["dragon", "attacks", "village"]


def test_extract_min_length():
    extractor = EntityExtractor(min_length=4)

    result = extractor.extract("the dragon is big")

    assert result == ["dragon"]


def test_extract_empty():
    extractor = EntityExtractor()

    result = extractor.extract("")

    assert result == []


def test_extract_lowercase():
    extractor = EntityExtractor()

    result = extractor.extract("Dragon FIRE")

    assert result == ["dragon", "fire"]


def test_extract_with_punctuation():
    extractor = EntityExtractor()

    result = extractor.extract("Dragon, attacks! village?")

    assert result == ["dragon", "attacks", "village"]


def test_extract_numbers():
    extractor = EntityExtractor()

    result = extractor.extract("dragon 123 village")

    assert result == ["dragon", "123", "village"]
