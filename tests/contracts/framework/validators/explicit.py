from packages.features.embedding_gateway.contracts import (
    EmbeddingGatewayContract as EmbeddingGateway,
)
from packages.features.llm_gateway.contracts import LLMGatewayContract
from packages.features.vector_index.contracts import (
    VectorIndexGateway,
    VectorReaderPort,
    VectorWriterPort,
)
from tests.contracts.framework.rules.base_rule import BaseRule
from tests.contracts.framework.rules.port_compliance_rule import ensure_port_compliance


class ExplicitPortsRule(BaseRule):
    name = "explicit_ports"

    def validate(self, container):
        # --------------------------------------------------
        # CORE PORTS
        # --------------------------------------------------
        ensure_port_compliance(container.llm, LLMGatewayContract, "llm")
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
