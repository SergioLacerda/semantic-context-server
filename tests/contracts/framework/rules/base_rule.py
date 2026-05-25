# tests/contracts/framework/rules/base_rule.py

from typing import Any


class BaseRule:
    name: str = "base"

    def validate(self, container: Any) -> None:
        raise NotImplementedError
