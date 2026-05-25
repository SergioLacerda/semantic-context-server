# tests/contracts/framework/validator.py

from typing import Any

from tests.contracts.framework.rules.port_compliance_rule import ensure_port_compliance
from tests.contracts.framework.types import PortSpec
from tests.contracts.registry.port_registry import PORT_REGISTRY
from tests.contracts.registry.storage_registry import STORAGE_PORTS

PortInstance = tuple[str, Any, PortSpec]


class ArchitectureValidator:
    def validate_container(self, container: Any) -> None:
        discovered = self._discover_container_ports(container)

        assert discovered, "No ports discovered in container"

        for name, instance, spec in discovered:
            self._validate(instance, spec.port, name)

    async def validate_storage(self, container: Any) -> None:
        discovered = await self._discover_storage_ports(container)

        assert discovered, "No storage ports discovered"

        for name, instance, spec in discovered:
            self._validate(instance, spec.port, name)

    def validate_coverage(self, container: Any) -> None:
        missing = []

        for name in PORT_REGISTRY:
            if not hasattr(container, name):
                missing.append(name)

        if missing:
            raise AssertionError(self._format_missing_ports(missing))

    def validate_explicit(self, container: Any) -> None:
        """
        Validação explícita (sanity check forte)
        """

        for name, spec in PORT_REGISTRY.items():
            if not hasattr(container, name):
                raise AssertionError(f"Missing explicit port: {name}")

            instance = getattr(container, name)

            self._validate(instance, spec.port, name)

    # ---------------------------------------------------------
    # DISCOVERY
    # ---------------------------------------------------------

    def _discover_container_ports(self, container: Any) -> list[PortInstance]:
        found: list[PortInstance] = []

        for attr in dir(container):
            if attr.startswith("_"):
                continue

            if attr in PORT_REGISTRY:
                instance = getattr(container, attr)
                spec = PORT_REGISTRY[attr]

                found.append((attr, instance, spec))

        return found

    async def _discover_storage_ports(self, container: Any) -> list[PortInstance]:
        results: list[PortInstance] = []

        campaign = await container.campaigns.get("c1")
        storage = campaign.storage

        builders = {
            "document_store": storage.build_document_store,
            "vector_store": storage.build_vector_store,
            "metadata_store": storage.build_metadata_store,
            "token_store": storage.build_token_store,
        }

        for name, builder in builders.items():
            try:
                instance = builder()
                spec = STORAGE_PORTS[name]
                results.append((name, instance, spec))
            except Exception as e:
                raise AssertionError(f"[storage:{name}] failed to build adapter: {e}") from e

        return results

    # ---------------------------------------------------------
    # VALIDATION
    # ---------------------------------------------------------

    def _validate(self, instance: Any, port: type, name: str):
        try:
            ensure_port_compliance(instance, port, name)
        except Exception as e:
            raise AssertionError(self._format_error(name, port, e)) from e

    # ---------------------------------------------------------
    # FORMATTERS
    # ---------------------------------------------------------

    def _format_error(self, name: str, port: type, error: Exception) -> str:
        return (
            f"\n[PORT VALIDATION ERROR]\nPort: {name}\nExpected: {port.__name__}\nError: {error}\n"
        )

    def _format_missing_ports(self, missing: list[str]) -> str:
        return "\n[MISSING PORTS]\n" + "\n".join(f"- {p}" for p in missing)
