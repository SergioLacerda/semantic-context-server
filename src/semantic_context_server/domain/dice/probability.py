from typing import Any

from semantic_context_server.domain.dice.analysis.solver_fft import FFTDiceSolver


def analyze_distribution(ast: Any) -> Any:
    solver = FFTDiceSolver()
    return solver.solve(ast)
