from tests.contracts.framework.rules.base_rule import BaseRule
from tests.contracts.framework.rules.port_compliance_rule import ensure_port_compliance
from tests.contracts.registry.port_registry import PORT_REGISTRY


class PortsRule(BaseRule):
    name = "ports"

    def validate(self, container):
        found = []

        for attr in dir(container):
            if attr.startswith("_"):
                continue

            if attr in PORT_REGISTRY:
                instance = getattr(container, attr)
                spec = PORT_REGISTRY[attr]

                ensure_port_compliance(instance, spec.port, attr)

                found.append(attr)

        if not found:
            raise AssertionError("No ports discovered")
