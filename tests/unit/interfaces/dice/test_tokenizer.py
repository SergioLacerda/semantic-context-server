import pytest

from semantic_context_server.domain.dice.ast.nodes import RerollNode
from semantic_context_server.domain.dice.parser import DiceParser
from semantic_context_server.interfaces.dice.tokenizer import normalize_expression


@pytest.fixture
def parser():
    return DiceParser()


# --------------------------------------------------
# NORMALIZATION
# --------------------------------------------------


def test_normalize_expression_trims_spaces():
    result = normalize_expression("  2d6  ")
    assert result == "2d6"


def test_normalize_expression_no_change():
    result = normalize_expression("2d6")
    assert result == "2d6"


# --------------------------------------------------
# PARSER INTEGRATION (leve)
# --------------------------------------------------


def test_parse_combined_rules(parser):
    node = parser.parse("4d6!kh3r<2")

    assert node is not None


# --------------------------------------------------
# REROLL LOGIC
# --------------------------------------------------


def test_reroll_condition_logic(parser):
    node = parser.parse("1d6r<3")

    assert isinstance(node, RerollNode)

    condition = node.condition

    assert condition(1) is True
    assert condition(4) is False
