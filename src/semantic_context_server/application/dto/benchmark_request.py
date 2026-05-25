from pydantic import BaseModel


class BenchmarkRequest(BaseModel):
    mode: str = "io"
    n: int = 50
    batch: bool = False
    cpu_work: int = 2_000_000
    workers: int | None = None
    dedup: bool = True
