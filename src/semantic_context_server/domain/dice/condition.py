from semantic_context_server.domain.dice.ast.nodes import DiceCondition


class _Condition(DiceCondition):
    def __init__(self, cond: str) -> None:
        self.cond = cond.strip()

    def __call__(self, v: int) -> bool:
        cond = self.cond

        if "<=" in cond:
            return v <= int(cond.split("<=")[1])

        if ">=" in cond:
            return v >= int(cond.split(">=")[1])

        if "<" in cond:
            return v < int(cond.split("<")[1])

        if ">" in cond:
            return v > int(cond.split(">")[1])

        return False
