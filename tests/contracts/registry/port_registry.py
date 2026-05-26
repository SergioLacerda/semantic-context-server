from packages.features.embedding_gateway.contracts import (
    EmbeddingGatewayContract as EmbeddingGateway,
)
from packages.features.llm_gateway.contracts import LLMGatewayContract
from packages.features.vector_index.contracts import (
    VectorIndexGateway,
    VectorReaderPort,
    VectorWriterPort,
)
from tests.contracts.framework.types import PortSpec

PORT_REGISTRY: dict[str, PortSpec] = {
    "llm": PortSpec("llm", LLMGatewayContract),
    "embedding": PortSpec("embedding", EmbeddingGateway),
    # --------------------------------------------------
    # VECTOR (NEW ARCH)
    # --------------------------------------------------
    "vector_writer": PortSpec("vector_writer", VectorWriterPort),
    "vector_reader": PortSpec("vector_reader", VectorReaderPort),
    # --------------------------------------------------
    # LOW-LEVEL INFRA
    # --------------------------------------------------
    "vector_index": PortSpec("vector_index", VectorIndexGateway),
}
