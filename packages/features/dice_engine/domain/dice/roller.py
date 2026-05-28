from typing import Protocol, runtime_checkable

from .value_objects import DiceExpression


@runtime_checkable
class RandomProvider(Protocol):
    def roll(self, sides: int) -> int: ...


def roll_dice(expr: DiceExpression, rng: RandomProvider) -> int:
    total = 0

    for _ in range(expr.quantity):
        value = rng.roll(expr.sides)
        total += value

    return total + expr.modifier
