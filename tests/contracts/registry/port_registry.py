from semantic_context_server.application.ports.embedding_gateway import EmbeddingGateway
from semantic_context_server.application.ports.llm import LLMServicePort
from semantic_context_server.application.ports.vector_index_gateway import VectorIndexGateway
from semantic_context_server.application.ports.vector_reader_port import VectorReaderPort
from semantic_context_server.application.ports.vector_writer_port import VectorWriterPort
from tests.contracts.framework.types import PortSpec

PORT_REGISTRY: dict[str, PortSpec] = {
    "llm": PortSpec("llm", LLMServicePort),
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
