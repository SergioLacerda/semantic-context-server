from collections.abc import Sequence
from typing import Any

import numpy as np


def cosine_similarity(a: Sequence[float] | Any, b: Sequence[float] | Any) -> float:
    """
    Similaridade de cosseno robusta.

    Aceita:
    - list[float]
    - numpy array
    """

    if a is None or b is None:
        return 0.0

    a_arr = np.array(a)
    b_arr = np.array(b)

    denom = (np.linalg.norm(a_arr) * np.linalg.norm(b_arr)) + 1e-8

    if denom == 0:
        return 0.0

    return float(np.dot(a_arr, b_arr) / denom)


def batch_cosine_similarity(
    query_vec: Sequence[float] | Any, vectors: Sequence[Sequence[float]]
) -> list[float]:
    q = np.array(query_vec)
    q_norm = np.linalg.norm(q) + 1e-8

    results: list[float] = []

    for v in vectors:
        v_arr = np.array(v)
        score = float(np.dot(q, v_arr) / (q_norm * (np.linalg.norm(v_arr) + 1e-8)))
        results.append(score)

    return results
