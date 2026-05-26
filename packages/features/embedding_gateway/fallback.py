from __future__ import annotations

import hashlib
import random


def deterministic_vector(text: str, dim: int) -> list[float]:
    seed = int(hashlib.sha256(text.encode()).hexdigest(), 16) % (2**32)
    rnd = random.Random(seed)
    return [rnd.uniform(-1, 1) for _ in range(dim)]


class VectorSpace:
    def __init__(self, target_dim: int) -> None:
        self.target_dim = target_dim

    def normalize(self, vec: list[float]) -> list[float]:
        if len(vec) == self.target_dim:
            return vec
        if len(vec) > self.target_dim:
            return vec[: self.target_dim]
        return vec + [0.0] * (self.target_dim - len(vec))
