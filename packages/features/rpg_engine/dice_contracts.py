from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol, runtime_checkable


@dataclass
class DiceResponse:
    text: str
    type: str = "dice"
    metadata: dict[str, Any] | None = None


@runtime_checkable
class DiceParserContract(Protocol):
    def parse(self, expression: str) -> Any: ...


@runtime_checkable
class DiceRollerContract(Protocol):
    def roll(self, ast: Any, rng: Any) -> tuple[list[int], int]: ...


@runtime_checkable
class DiceDistributionAnalyzerContract(Protocol):
    def analyze(self, ast: Any) -> Any: ...


@runtime_checkable
class DiceResponseMapperContract(Protocol):
    def map(self, rolls: list[int], total: int, distribution: Any | None) -> DiceResponse: ...

