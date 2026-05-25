from typing import Any

import numpy as np

from semantic_context_server.domain.dice.ast.nodes import (
    DropLowestNode,
    ExplodeNode,
    KeepHighestNode,
    Node,
    RerollNode,
    RollNode,
)


class FFTDiceSolver:
    def __init__(self, max_explode_depth: int = 50):
        self.max_explode_depth = max_explode_depth
        self._cache: dict[str, np.ndarray] = {}

    # ========================
    # PUBLIC API
    # ========================
    def solve(self, node: Node) -> np.ndarray:
        self._cache.clear()
        return self._solve_node(node)

    # ========================
    # CACHE + DISPATCH
    # ========================
    def _solve_node(self, node: Node) -> np.ndarray:
        key = repr(node)

        if key in self._cache:
            return self._cache[key]

        result = self._compute_node(node)
        result = self._trim(result)

        self._cache[key] = result
        return result

    # ========================
    # CORE
    # ========================
    def _compute_node(self, node: Node) -> np.ndarray:
        if isinstance(node, RollNode):
            base = self._single_die(node.sides)
            return self._power(base, node.quantity)

        if isinstance(node, ExplodeNode):
            base = self._solve_node(node.child)
            return base

        if isinstance(node, RerollNode):
            base = self._solve_node(node.child)
            return base

        if isinstance(node, KeepHighestNode):
            return self._keep_highest_node(node)

        if isinstance(node, DropLowestNode):
            return self._drop_lowest_node(node)

        raise NotImplementedError(type(node))

    # ========================
    # LOW LEVEL
    # ========================
    def _single_die(self, sides: int) -> np.ndarray:
        dist = np.zeros(sides + 1)
        dist[1:] = 1.0 / sides
        return dist

    def _normalize(self, dist: np.ndarray) -> np.ndarray:
        s = dist.sum()
        return dist if s == 0 else dist / s

    def _fft_convolve(self, a: np.ndarray, b: np.ndarray) -> np.ndarray:
        size = len(a) + len(b) - 1
        n = 1 << (size - 1).bit_length()

        fa = np.fft.rfft(a, n)
        fb = np.fft.rfft(b, n)

        result = np.fft.irfft(fa * fb, n)
        return np.maximum(result[:size], 0)

    def _power(self, base: np.ndarray, n: int) -> np.ndarray:
        result = np.array([1.0])
        power = base.copy()

        while n > 0:
            if n & 1:
                result = self._fft_convolve(result, power)
            power = self._fft_convolve(power, power)
            n >>= 1

        return self._normalize(result)

    # ========================
    # REROLL
    # ========================
    def _apply_reroll(self, base: np.ndarray, condition: Any) -> np.ndarray:
        mask = np.array([condition(i) for i in range(len(base))])
        reroll_prob = base[mask].sum()

        new_dist = base.copy()
        new_dist[mask] = 0
        new_dist += reroll_prob * base

        return self._normalize(new_dist)

    # ========================
    # EXPLODE (DIST)
    # ========================
    def _explode_dist(self, base: np.ndarray) -> np.ndarray:
        p_explode = base[-1]

        result = np.zeros_like(base)
        current = base.copy()

        for _ in range(self.max_explode_depth):
            if len(result) < len(current):
                result = np.pad(result, (0, len(current) - len(result)))

            result[: len(current)] += current

            current = self._fft_convolve(current, base) * p_explode

            if current.sum() < 1e-10:
                break

        return self._normalize(result)

    # ========================
    # KEEP / DROP (SAMPLING)
    # ========================

    def _drop_lowest_node(self, node: DropLowestNode) -> np.ndarray:
        base = self._solve_node(node.child)
        return self._drop_lowest_from_dist(base, node.k)

    def _keep_highest_node(self, node: KeepHighestNode) -> np.ndarray:
        base = self._solve_node(node.child)
        return self._keep_highest_from_dist(base, node.k)

    def _keep_highest_from_dist(self, base: np.ndarray, k: int, samples: int = 20000) -> np.ndarray:
        rng = np.random.default_rng()

        values = np.arange(len(base))
        probs = base

        results = np.zeros(samples, dtype=int)

        for i in range(samples):
            rolls = rng.choice(values, size=k, p=probs)
            results[i] = np.sum(rolls)

        return self._histogram(results)

    def _drop_lowest_from_dist(self, base: np.ndarray, k: int, samples: int = 20000) -> np.ndarray:
        rng = np.random.default_rng()

        values = np.arange(len(base))
        probs = base

        results = np.zeros(samples, dtype=int)

        for i in range(samples):
            rolls = rng.choice(values, size=k, p=probs)
            results[i] = np.sum(rolls)

        return self._histogram(results)

    def _keep_highest_sampling(
        self, base: np.ndarray, n: int, k: int, samples: int = 20000
    ) -> np.ndarray:
        rng = np.random.default_rng()
        sides = len(base) - 1
        probs = base[1:]

        results = np.zeros(samples, dtype=int)

        for i in range(samples):
            rolls = rng.choice(np.arange(1, sides + 1), size=n, p=probs)
            rolls.sort()
            results[i] = np.sum(rolls[-k:])

        return self._histogram(results)

    def _drop_lowest_sampling(
        self, base: np.ndarray, n: int, k: int, samples: int = 20000
    ) -> np.ndarray:
        rng = np.random.default_rng()
        sides = len(base) - 1
        probs = base[1:]

        results = np.zeros(samples, dtype=int)

        for i in range(samples):
            rolls = rng.choice(np.arange(1, sides + 1), size=n, p=probs)
            rolls.sort()
            results[i] = np.sum(rolls[k:])

        return self._histogram(results)

    def _histogram(self, results: np.ndarray) -> np.ndarray:
        max_sum = results.max()
        dist = np.zeros(max_sum + 1)

        for r in results:
            dist[r] += 1

        return self._normalize(dist)

    # ========================
    # TRIM (PRUNE)
    # ========================
    def _trim(self, dist: np.ndarray, threshold: float = 1e-10) -> np.ndarray:
        mask = dist > threshold

        if not mask.any():
            return dist

        last = np.max(np.where(mask))
        return dist[: last + 1]
