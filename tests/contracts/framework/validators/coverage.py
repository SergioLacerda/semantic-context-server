from tests.contracts.framework.rules.base_rule import BaseRule
from tests.contracts.registry.port_registry import PORT_REGISTRY


class CoverageRule(BaseRule):
    name = "coverage"

    def validate(self, container):
        missing = [name for name in PORT_REGISTRY if not hasattr(container, name)]

        if missing:
            raise AssertionError(f"Missing ports: {missing}")
