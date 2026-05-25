from semantic_context_server.application.ports.embedding_gateway import EmbeddingGateway
from semantic_context_server.application.ports.llm import LLMServicePort
from semantic_context_server.application.ports.vector_index_gateway import VectorIndexGateway
from semantic_context_server.application.ports.vector_reader_port import VectorReaderPort
from semantic_context_server.application.ports.vector_writer_port import VectorWriterPort
from tests.contracts.framework.rules.base_rule import BaseRule
from tests.contracts.framework.rules.port_compliance_rule import ensure_port_compliance


class ExplicitPortsRule(BaseRule):
    name = "explicit_ports"

    def validate(self, container):
        # --------------------------------------------------
        # CORE PORTS
        # --------------------------------------------------
        ensure_port_compliance(container.llm, LLMServicePort, "llm")
        ensure_port_compliance(container.embedding, EmbeddingGateway, "embedding")

        # --------------------------------------------------
        # VECTOR (NEW ARCH)
        # --------------------------------------------------
        ensure_port_compliance(container.vector_writer, VectorWriterPort, "vector_writer")
        ensure_port_compliance(container.vector_reader, VectorReaderPort, "vector_reader")

        # --------------------------------------------------
        # LOW-LEVEL INDEX (INFRA PORT)
        # --------------------------------------------------
        ensure_port_compliance(container.vector_index, VectorIndexGateway, "vector_index")
