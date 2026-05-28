from dataclasses import dataclass
from typing import Protocol

# ---------------------------------------------------------
# BASE NODE
# ---------------------------------------------------------


class DiceNode:
    """Base class for all dice AST nodes."""

    ...


# ---------------------------------------------------------
# CONDITION
# ---------------------------------------------------------


class DiceCondition(Protocol):
    def __call__(self, value: int) -> bool: ...


# ---------------------------------------------------------
# BASE ROLL
# ---------------------------------------------------------


@dataclass(slots=True)
class RollNode(DiceNode):
    quantity: int
    sides: int


# ---------------------------------------------------------
# OPERATIONS (PIPELINE)
# ---------------------------------------------------------


@dataclass(slots=True)
class ExplodeNode(DiceNode):
    child: "Node"


@dataclass(slots=True)
class RerollNode(DiceNode):
    child: "Node"
    condition: DiceCondition


@dataclass(slots=True)
class KeepHighestNode(DiceNode):
    child: "Node"
    k: int


@dataclass(slots=True)
class DropLowestNode(DiceNode):
    child: "Node"
    k: int


# ---------------------------------------------------------
# UNION
# ---------------------------------------------------------

Node = RollNode | ExplodeNode | RerollNode | KeepHighestNode | DropLowestNode
