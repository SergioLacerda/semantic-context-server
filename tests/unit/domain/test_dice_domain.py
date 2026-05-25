from dataclasses import FrozenInstanceError
from typing import Any, cast

import pytest

from semantic_context_server.domain.dice.value_objects import DiceExpression


def test_dice_expression_creation():
    expr = DiceExpression(quantity=2, sides=6, modifier=3)

    assert expr.quantity == 2
    assert expr.sides == 6
    assert expr.modifier == 3


def test_dice_expression_immutable():
    expr = DiceExpression(1, 6)

    with pytest.raises(FrozenInstanceError):
        cast(Any, expr).quantity = 2
