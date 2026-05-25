# domain/dice/rules.py
from semantic_context_server.domain.random.random_provider import RandomProvider

from .value_objects import DiceExpression


def roll_dice(expr: DiceExpression, rng: RandomProvider) -> int:
    total = 0

    for _ in range(expr.quantity):
        value = rng.roll(expr.sides)
        total += value

    return total + expr.modifier
