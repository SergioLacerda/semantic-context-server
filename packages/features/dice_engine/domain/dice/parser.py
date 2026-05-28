from .ast.nodes import (
    DiceCondition,
    DiceNode,
    DropLowestNode,
    ExplodeNode,
    KeepHighestNode,
    Node,
    RerollNode,
    RollNode,
)
from .condition import _Condition
from .dice_regex import DiceRegex


class DiceParser:
    def _build_condition(self, cond: str) -> DiceCondition:
        return _Condition(cond)

    def parse(self, expression: str) -> DiceNode:
        match = DiceRegex.match(expression)

        if not match:
            raise ValueError(f"Invalid dice expression: {expression}")

        # -------------------------
        # BASE
        # -------------------------
        num = int(match.group("num"))
        sides = int(match.group("sides"))

        node: Node = RollNode(num, sides)

        # -------------------------
        # EXPLODE (!)
        # -------------------------
        if match.group("explode"):
            node = ExplodeNode(node)

        # -------------------------
        # KEEP (khX)
        # -------------------------
        keep = match.group("keep")
        if keep:
            try:
                k = int(keep[2:])
                node = KeepHighestNode(node, k)
            except ValueError as err:
                raise ValueError(f"Invalid keep modifier: {keep}") from err

        # -------------------------
        # DROP (dlX)
        # -------------------------
        drop = match.group("drop")
        if drop:
            try:
                k = int(drop[2:])
                node = DropLowestNode(node, k)
            except ValueError as err:
                raise ValueError(f"Invalid keep modifier: {keep}") from err

        # -------------------------
        # REROLL (r<3, r>=2, etc)
        # -------------------------
        reroll = match.group("reroll")
        if reroll:
            node = RerollNode(node, self._build_condition(reroll))

        return node

    # --------------------------------------------------
    # CONDITION BUILDER
    # --------------------------------------------------
