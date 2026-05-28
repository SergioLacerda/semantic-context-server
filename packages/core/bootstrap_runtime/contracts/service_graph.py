from __future__ import annotations

from typing import Any


class DuplicateRegistrationError(ValueError):
    pass


class UnregisteredPortError(KeyError):
    pass


class ServiceGraph:
    def __init__(self) -> None:
        self._data: dict[type[Any], Any] = {}

    def register(self, port: type[Any], instance: Any) -> None:
        if port in self._data and self._data[port] is not instance:
            raise DuplicateRegistrationError(f"Port already registered: {port}")
        self._data[port] = instance

    def resolve(self, port: type[Any]) -> Any:
        if port not in self._data:
            raise UnregisteredPortError(f"Port not registered: {port}")
        return self._data[port]

    def has(self, port: type[Any]) -> bool:
        return port in self._data

    def items(self) -> list[tuple[type[Any], Any]]:
        return list(self._data.items())
