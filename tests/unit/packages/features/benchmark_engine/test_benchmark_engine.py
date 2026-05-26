from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve()
while PROJECT_ROOT != PROJECT_ROOT.parent and not (PROJECT_ROOT / "pyproject.toml").exists():
    PROJECT_ROOT = PROJECT_ROOT.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from packages.features.benchmark_engine import BenchmarkEngineService  # noqa: E402


class FakeBenchmarkRunner:
    async def run(self, mode: str, n: int, batch: bool, **kwargs):
        return {"mode": mode, "n": n, "batch": batch, "status": "ok", "extra": kwargs}


async def test_benchmark_engine_isolated_service() -> None:
    svc = BenchmarkEngineService(FakeBenchmarkRunner())
    out = await svc.run(mode="io", n=10, batch=False, strategy="concurrent")
    assert out["status"] == "ok"
    assert out["extra"]["strategy"] == "concurrent"
