def compute_score(report: dict) -> float:
    if "error" in report:
        return float("inf")

    return float(report["p95"] * 0.6 + report["avg"] * 0.3 - report["throughput"] * 0.1)


def rank_strategies(results: dict) -> list[tuple[str, dict]]:
    return sorted(results.items(), key=lambda item: compute_score(item[1]))


def extract_winner(ranking: list[tuple[str, dict]]) -> str | None:
    if not ranking:
        return None
    return ranking[0][0]
