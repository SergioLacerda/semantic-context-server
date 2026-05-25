from semantic_context_server.application.services.benchmark_formatter import (
    BenchmarkFormatter,
)


def test_format_report_empty():
    fmt = BenchmarkFormatter()

    result = fmt.format_report({})

    assert result == "No data available."


def test_format_report_values():
    fmt = BenchmarkFormatter()

    report = {
        "avg": 1.23456,
        "count": 10,
    }

    result = fmt.format_report(report)

    assert "avg: 1.2346" in result
    assert "count: 10" in result


def test_format_compare_empty():
    fmt = BenchmarkFormatter()

    result = fmt.format_compare({})

    assert result == "No comparison results."


def test_format_compare_with_error():
    fmt = BenchmarkFormatter()

    results = {"mode1": {"error": "fail"}}

    result = fmt.format_compare(results)

    assert "ERROR: fail" in result


def test_format_compare_normal():
    fmt = BenchmarkFormatter()

    results = {"mode1": {"avg": 1.2345}}

    result = fmt.format_compare(results)

    assert "[MODE1]" in result
    assert "avg: 1.2345" in result


def test_format_strategies_empty():
    fmt = BenchmarkFormatter()

    result = fmt.format_strategies({})

    assert result == "No strategy results."


def test_format_strategies_ranking_and_winner():
    fmt = BenchmarkFormatter()

    data = {
        "ranking": [
            ("a", {"p95": 10, "avg": 5, "throughput": 2}),
        ],
        "winner": "a",
    }

    result = fmt.format_strategies(data)

    assert "🏆 Ranking" in result
    assert "1. a" in result
    assert "🥇 Winner: a" in result


def test_format_strategies_details_with_error():
    fmt = BenchmarkFormatter()

    data = {"results": {"x": {"error": "boom"}}}

    result = fmt.format_strategies(data)

    assert "[x]" in result
    assert "ERROR: boom" in result


def test_format_strategies_details_normal():
    fmt = BenchmarkFormatter()

    data = {"results": {"x": {"avg": 1.2345}}}

    result = fmt.format_strategies(data)

    assert "avg: 1.2345" in result


def test_safe_score_error():
    fmt = BenchmarkFormatter()

    score = fmt._safe_score({"error": "fail"})

    assert score == float("inf")


def test_safe_score_normal():
    fmt = BenchmarkFormatter()

    report = {"p95": 10, "avg": 5, "throughput": 2}

    score = fmt._safe_score(report)

    assert score == 10 * 0.6 + 5 * 0.3 - 2 * 0.1


def test_safe_score_missing_fields():
    fmt = BenchmarkFormatter()

    score = fmt._safe_score({})

    assert score == 0.0
