from typing import Protocol

from semantic_context_server.domain.dice.ast.nodes import (
    DiceNode,
    DropLowestNode,
    ExplodeNode,
    KeepHighestNode,
    RerollNode,
    RollNode,
)
from semantic_context_server.domain.dice.rules.explode import explode
from semantic_context_server.domain.dice.rules.keep_drop import (
    drop_lowest,
    keep_highest,
)
from semantic_context_server.domain.dice.rules.reroll import reroll


class RNG(Protocol):
    def roll(self, sides: int) -> int: ...


def _extract_sides(node: DiceNode) -> int:
    if hasattr(node, "sides"):
        return int(node.sides)
    if hasattr(node, "child"):
        return _extract_sides(node.child)
    raise ValueError("No sides found")


def evaluate(node: DiceNode, rng: RNG) -> list[int]:
    if isinstance(node, RollNode):
        return [rng.roll(node.sides) for _ in range(node.quantity)]

    if isinstance(node, ExplodeNode):
        base = evaluate(node.child, rng)
        sides = _extract_sides(node.child)
        return explode(base, sides, rng)

    if isinstance(node, RerollNode):
        base = evaluate(node.child, rng)
        sides = _extract_sides(node.child)
        return reroll(base, node.condition, sides, rng)

    if isinstance(node, KeepHighestNode):
        base = evaluate(node.child, rng)
        return keep_highest(base, node.k)

    if isinstance(node, DropLowestNode):
        base = evaluate(node.child, rng)
        return drop_lowest(base, node.k)

    raise ValueError(f"Unknown node: {node}")
