from abc import abstractmethod
from typing import Protocol, runtime_checkable


@runtime_checkable
class RandomProvider(Protocol):
    @abstractmethod
    def roll(self, sides: int) -> int:
        pass
