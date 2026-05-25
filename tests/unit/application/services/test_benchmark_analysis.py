from typing import Any

from semantic_context_server.application.services.benchmark_analysis import (
    compute_score,
    extract_winner,
    rank_strategies,
)


def test_compute_score_normal():
    report = {
        "p95": 100,
        "avg": 50,
        "throughput": 10,
    }

    score = compute_score(report)

    expected = 100 * 0.6 + 50 * 0.3 - 10 * 0.1
    assert score == expected


def test_compute_score_with_error():
    report = {"error": "fail"}

    score = compute_score(report)

    assert score == float("inf")


def test_rank_strategies():
    results = {
        "a": {"p95": 100, "avg": 50, "throughput": 10},
        "b": {"p95": 50, "avg": 20, "throughput": 5},
    }

    ranking = rank_strategies(results)

    assert ranking[0][0] == "b"


def test_rank_strategies_with_error():
    results = {
        "good": {"p95": 50, "avg": 20, "throughput": 5},
        "bad": {"error": "fail"},
    }

    ranking = rank_strategies(results)

    assert ranking[-1][0] == "bad"


def test_extract_winner():
    ranking: list[tuple[str, dict[str, Any]]] = [
        ("a", {}),
        ("b", {}),
    ]

    winner = extract_winner(ranking)

    assert winner == "a"


def test_extract_winner_empty():
    winner = extract_winner([])

    assert winner is None
