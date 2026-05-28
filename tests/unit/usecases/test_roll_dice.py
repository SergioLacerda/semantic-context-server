from typing import Any

import pytest

from packages.features.dice_engine import DiceUseCase


class MockRng:
    def roll(self, sides: int) -> int:
        return max(1, min(sides, 3))


class MockParser:
    def __init__(self, result: Any = None, error: bool = False):
        self.result = result
        self.error = error

    def parse(self, expression: str) -> Any:
        if self.error:
            raise ValueError("parse error")
        return self.result


class MockRoller:
    def __init__(self, rolls: list[int] | None = None, fail: bool = False):
        self.rolls = rolls or [1]
        self.fail = fail

    def roll(self, ast: Any, rng: Any) -> tuple[list[int], int]:
        if self.fail:
            raise Exception("boom")
        return self.rolls, sum(self.rolls)


class MockAnalyzer:
    def __init__(self, result: Any = None, fail: bool = False):
        self.result = result if result is not None else {"p": [1.0]}
        self.fail = fail

    def analyze(self, ast: Any) -> Any:
        if self.fail:
            raise Exception("analysis boom")
        return self.result


class FakeAST:
    def evaluate(self):
        return 42


@pytest.mark.unit
@pytest.mark.asyncio
async def test_roll_dice_invalid_expression_returns_error():
    usecase = DiceUseCase(
        rng=MockRng(),
        parser=MockParser(result=None),
        roller=MockRoller(),
        analyzer=MockAnalyzer(),
        executor=None,
        enable_analysis=False,
    )

    result = await usecase.execute("invalid")

    assert result.type == "error"
    assert (result.metadata or {}).get("error") == "Invalid dice expression"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_roll_dice_with_string_expression():
    usecase = DiceUseCase(
        rng=MockRng(),
        parser=MockParser(result=FakeAST()),
        roller=MockRoller([2, 4]),
        analyzer=MockAnalyzer(),
        executor=None,
        enable_analysis=False,
    )

    result = await usecase.execute("1d6")

    assert result.type == "dice"
    assert result.metadata is not None
    assert result.metadata["total"] == 6
    assert result.metadata["rolls"] == [2, 4]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_roll_dice_with_ast_expression():
    usecase = DiceUseCase(
        rng=MockRng(),
        parser=MockParser(),
        roller=MockRoller([3, 3]),
        analyzer=MockAnalyzer(),
        executor=None,
        enable_analysis=False,
    )

    result = await usecase.execute(FakeAST())

    assert result.type == "dice"
    assert result.metadata is not None
    assert result.metadata["total"] == 6


@pytest.mark.unit
@pytest.mark.asyncio
async def test_roll_dice_with_analysis_enabled():
    usecase = DiceUseCase(
        rng=MockRng(),
        parser=MockParser(result=FakeAST()),
        roller=MockRoller([1, 5]),
        analyzer=MockAnalyzer(result={"p": [0.5, 0.5]}),
        executor=None,
        enable_analysis=True,
    )

    result = await usecase.execute("1d6")

    assert result.metadata is not None
    assert "distribution" in result.metadata
    assert result.metadata["distribution"] == {"p": [0.5, 0.5]}


@pytest.mark.unit
@pytest.mark.asyncio
async def test_roll_dice_analysis_failure_returns_none_distribution():
    usecase = DiceUseCase(
        rng=MockRng(),
        parser=MockParser(result=FakeAST()),
        roller=MockRoller([1, 5]),
        analyzer=MockAnalyzer(fail=True),
        executor=None,
        enable_analysis=True,
    )

    result = await usecase.execute("1d6")

    assert result.type == "dice"
    assert result.metadata is not None
    assert result.metadata.get("distribution") is None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_roll_exception_returns_error():
    usecase = DiceUseCase(
        rng=MockRng(),
        parser=MockParser(result=FakeAST()),
        roller=MockRoller(fail=True),
        analyzer=MockAnalyzer(),
        executor=None,
        enable_analysis=False,
    )

    result = await usecase.execute("2d6")

    assert result.type == "error"
    assert "Roll execution failed" in result.text


@pytest.mark.unit
@pytest.mark.asyncio
async def test_invalid_input_type_returns_error():
    usecase = DiceUseCase(
        rng=MockRng(),
        parser=MockParser(),
        roller=MockRoller(),
        analyzer=MockAnalyzer(),
        executor=None,
        enable_analysis=False,
    )

    result = await usecase.execute(123)

    assert result.type == "error"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_parse_exception_returns_error():
    usecase = DiceUseCase(
        rng=MockRng(),
        parser=MockParser(error=True),
        roller=MockRoller(),
        analyzer=MockAnalyzer(),
        executor=None,
        enable_analysis=False,
    )

    result = await usecase.execute("2d6")

    assert result.type == "error"
