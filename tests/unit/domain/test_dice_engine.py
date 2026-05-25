from semantic_context_server.domain.dice.dice_engine import roll


def test_roll_returns_expected_rolls_and_total(monkeypatch):
    def fake_evaluate(ast, rng):
        assert ast == "fake"
        return [3, 4]

    monkeypatch.setattr("semantic_context_server.domain.dice.dice_engine.evaluate", fake_evaluate)

    rolls, total = roll(ast="fake", rng=None)

    assert rolls == [3, 4]
    assert total == sum(rolls)
