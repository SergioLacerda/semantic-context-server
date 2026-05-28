# domain/dice/value_objects.py
from dataclasses import dataclass


@dataclass(frozen=True)
class DiceExpression:
    quantity: int
    sides: int
    modifier: int = 0
