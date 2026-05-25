# tests/contracts/registry/storage_registry.py


from tests.contracts.framework.types import PortSpec

STORAGE_PORTS: dict[str, PortSpec] = {
    "document_store": PortSpec("document_store", object),
    "vector_store": PortSpec("vector_store", object),
    "metadata_store": PortSpec("metadata_store", object),
    "token_store": PortSpec("token_store", object),
}
