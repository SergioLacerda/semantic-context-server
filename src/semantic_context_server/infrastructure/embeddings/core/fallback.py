import hashlib
import random


def deterministic_vector(text: str, dim: int) -> list[float]:
    seed = int(hashlib.sha256(text.encode()).hexdigest(), 16) % (2**32)
    rnd = random.Random(seed)

    return [rnd.uniform(-1, 1) for _ in range(dim)]
