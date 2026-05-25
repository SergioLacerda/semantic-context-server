from typing import Any

import pytest

from semantic_context_server.application.contracts.response import Response
from semantic_context_server.domain.dice.ast.nodes import RollNode
from semantic_context_server.domain.dice.value_objects import DiceExpression
from semantic_context_server.infrastructure.random.default_random import DefaultRandomProvider
from semantic_context_server.interfaces.dice.parser_adapter import DiceParserAdapter
from semantic_context_server.usecases.roll_dice import RollDiceUseCase

# ==========================================================
# MOCKS
# ==========================================================


class MockParser:
    def __init__(self, result: Any = None, error: bool = False):
        self.result = result
        self.error = error

    def parse(self, expression: str) -> Any:
        if self.error:
            raise ValueError("parse error")
        return self.result


# ---------------------------------------------------------
# HELPERS
# ---------------------------------------------------------


@pytest.fixture
def usecase():
    return RollDiceUseCase(
        rng=DefaultRandomProvider(),
        parser=DiceParserAdapter(),
        executor=None,
    )


def data(response: Response) -> dict:
    return response.metadata or {}


class FakeAST:
    def evaluate(self):
        return 42


@pytest.mark.unit
@pytest.mark.asyncio
async def test_roll_dice_invalid(usecase):
    result = await usecase.execute("invalid")

    assert result.type == "error"
    assert data(result)["error"] == "Invalid dice expression"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_roll_dice_usecase(usecase):
    result = await usecase.execute(DiceExpression(2, 6, 1))

    d = data(result)

    assert isinstance(d["total"], int)
    assert "rolls" in d


@pytest.mark.unit
@pytest.mark.asyncio
async def test_roll_dice_with_expression(usecase):
    result = await usecase.execute(DiceExpression(2, 6))

    assert data(result)["total"] > 0


@pytest.mark.unit
@pytest.mark.asyncio
async def test_roll_dice_with_analysis(usecase):
    usecase.enable_analysis = True

    result = await usecase.execute(DiceExpression(1, 6))

    assert "distribution" in data(result)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_roll_dice_analysis_failure(usecase, monkeypatch):
    monkeypatch.setattr(
        "semantic_context_server.application.usecases.roll_dice_usecase.analyze_distribution",
        lambda ast: (_ for _ in ()).throw(Exception()),
    )

    usecase.enable_analysis = True

    result = await usecase.execute(DiceExpression(1, 6))

    assert data(result)["distribution"] is None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_roll_dice_parser_path():
    class FakeParser:
        def parse(self, expr: str) -> Any:
            return RollNode(1, 6)

    usecase = RollDiceUseCase(
        rng=DefaultRandomProvider(),
        parser=FakeParser(),
        executor=None,
    )

    result = await usecase.execute("1d6")

    assert data(result)["total"] > 0


@pytest.mark.unit
@pytest.mark.asyncio
async def test_invalid_expression_returns_error():
    parser = MockParser(result=None)

    usecase = RollDiceUseCase(
        rng=None,
        parser=parser,
        executor=None,
    )

    result = await usecase.execute("invalid")

    assert result.type == "error"
    assert "Invalid dice expression" in result.text


@pytest.mark.unit
@pytest.mark.asyncio
async def test_invalid_type_returns_error():
    parser = MockParser()

    usecase = RollDiceUseCase(
        rng=None,
        parser=parser,
        executor=None,
    )

    result = await usecase.execute(123)

    assert result.type == "error"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_parse_exception():
    parser = MockParser(error=True)

    usecase = RollDiceUseCase(
        rng=None,
        parser=parser,
        executor=None,
    )

    result = await usecase.execute("2d6")

    assert result.type == "error"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_roll_exception(monkeypatch):
    parser = MockParser(result=FakeAST())

    usecase = RollDiceUseCase(
        rng=None,
        parser=parser,
        executor=None,
    )

    def fake_roll(ast, rng):
        raise Exception("boom")

    monkeypatch.setattr(
        "semantic_context_server.application.usecases.roll_dice_usecase.roll",
        fake_roll,
    )

    result = await usecase.execute("2d6")

    assert result.type == "error"
    assert "Roll execution failed" in result.text


@pytest.mark.unit
@pytest.mark.asyncio
async def test_expression_with_evaluate_method(monkeypatch):
    class CustomExpression:
        def evaluate(self):
            return 42

    class MockParserLocal:
        def parse(self, expression: str) -> Any:
            return None

    usecase = RollDiceUseCase(
        rng=None,
        parser=MockParserLocal(),
        executor=None,
    )

    def fake_roll(ast, rng):
        return [1, 2, 3], 6

    monkeypatch.setattr(
        "semantic_context_server.application.usecases.roll_dice_usecase.roll",
        fake_roll,
    )

    result = await usecase.execute(CustomExpression())

    assert result.type == "dice"
    assert result.metadata is not None
    assert result.metadata["total"] == 6
