import asyncio
import random

import pytest

from semantic_context_server.application.ports.executor import ExecutorPort
from semantic_context_server.infrastructure.serialization.json_serializer import JSONSerializer
from semantic_context_server.infrastructure.storage.adapters.base_json_adapter import (
    BaseJsonAdapter,
)


@pytest.mark.asyncio
async def test_base_json_adapter_stress_contention(tmp_path, container):
    """
    Stress test para validar a contenção do threading.Lock e atomicidade no BaseJsonAdapter.
    Dispara múltiplas escritas concorrentes no mesmo arquivo para garantir integridade.
    """
    # 1. Setup
    executor = container.resolve(ExecutorPort)
    serializer = JSONSerializer()
    file_path = tmp_path / "campaign_stress.json"

    # Instanciamos o adaptador diretamente para isolar o teste de estresse
    adapter = BaseJsonAdapter(file_path, executor, serializer)

    num_iterations = 100

    async def write_task(i):
        # jitter para aumentar a probabilidade de colisão no Lock
        await asyncio.sleep(random.uniform(0, 0.05))

        data = {"iteration": i, "payload": "heavy_data_" * 100, "timestamp": random.random()}

        try:
            await adapter._write_file(data)
        except Exception as e:
            pytest.fail(f"Atomic write failed at iteration {i}: {e}")

    # 2. Execução: 100 tarefas tentando escrever no mesmo arquivo via ThreadPool
    tasks = [write_task(i) for i in range(num_iterations)]
    await asyncio.gather(*tasks)

    # 3. Validação
    # O arquivo deve ser um JSON válido e conter a estrutura correta.
    # Se a atomicidade falhasse, o JSON estaria quebrado ou incompleto.
    content = await adapter._read_file()
    assert content is not None
    assert "iteration" in content
    assert 0 <= content["iteration"] < num_iterations
