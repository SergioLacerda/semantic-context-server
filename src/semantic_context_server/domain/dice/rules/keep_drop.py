def keep_highest(values: list[int], k: int) -> list[int]:
    return sorted(values, reverse=True)[:k]


def drop_lowest(values: list[int], k: int) -> list[int]:
    return sorted(values)[k:]
