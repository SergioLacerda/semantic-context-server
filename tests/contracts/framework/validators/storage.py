from tests.contracts.framework.rules.base_rule import BaseRule
from tests.contracts.framework.rules.port_compliance_rule import ensure_port_compliance
from tests.contracts.registry.storage_registry import STORAGE_PORTS


class StorageRule(BaseRule):
    name = "storage"

    def validate(self, container):
        campaign = await container.campaigns.get("c1")
        storage = campaign.storage

        builders = {
            "document_store": storage.build_document_store,
            "vector_store": storage.build_vector_store,
            "metadata_store": storage.build_metadata_store,
            "token_store": storage.build_token_store,
        }

        for name, builder in builders.items():
            instance = builder()
            spec = STORAGE_PORTS[name]

            ensure_port_compliance(instance, spec.port, name)
