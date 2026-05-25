from typing import Any


def reroll(values: list[int], condition: Any, sides: int, rng: Any) -> list[int]:
    result = []

    for v in values:
        while condition(v):
            v = rng.roll(sides)
        result.append(v)

    return result
