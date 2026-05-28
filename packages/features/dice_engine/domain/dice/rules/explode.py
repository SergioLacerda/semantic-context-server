from typing import Any


def explode(values: list[int], sides: int, rng: Any) -> list[int]:
    result = []

    for v in values:
        result.append(v)

        while v == sides:
            v = rng.roll(sides)
            result.append(v)

    return result
