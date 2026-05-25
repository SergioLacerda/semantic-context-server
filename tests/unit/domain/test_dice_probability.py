from semantic_context_server.domain.dice.probability import analyze_distribution


class FakeSolver:
    def solve(self, ast):
        return {"min": 1, "max": 6}


def test_analyze_distribution(monkeypatch):
    monkeypatch.setattr(
        "semantic_context_server.domain.dice.probability.FFTDiceSolver",
        lambda: FakeSolver(),
    )

    result = analyze_distribution(ast="fake")

    assert result["min"] == 1
    assert result["max"] == 6
