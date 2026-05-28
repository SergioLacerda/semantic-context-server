from typing import Any

from .rules.evaluator import evaluate


def roll(ast: Any, rng: Any) -> tuple[list[int], int]:
    """
    Executa rolagem a partir de um AST (não string).
    """

    rolls = evaluate(ast, rng)
    total = sum(rolls)

    return rolls, total
