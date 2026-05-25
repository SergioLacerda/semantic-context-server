# tests/contracts/framework/types.py

from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")


@dataclass(frozen=True)
class PortSpec(Generic[T]):
    name: str
    port: type[T]
