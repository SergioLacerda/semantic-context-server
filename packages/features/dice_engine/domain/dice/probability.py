from typing import Any

from .analysis.solver_fft import FFTDiceSolver


def analyze_distribution(ast: Any) -> Any:
    solver = FFTDiceSolver()
    return solver.solve(ast)
