from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve()
while PROJECT_ROOT != PROJECT_ROOT.parent and not (PROJECT_ROOT / "pyproject.toml").exists():
    PROJECT_ROOT = PROJECT_ROOT.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from packages.features.llm_gateway import LLMGatewayService  # noqa: E402


class FakeLLMProvider:
    async def generate(self, request):
        return {"provider": "fake", "request": request}


async def test_llm_gateway_service_routes_to_default_provider() -> None:
    svc = LLMGatewayService({"fake": FakeLLMProvider()}, default_provider="fake")
    out = await svc.generate({"prompt": "hello"})
    assert out["provider"] == "fake"
