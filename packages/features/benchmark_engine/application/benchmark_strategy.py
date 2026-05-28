from dataclasses import dataclass


@dataclass
class BenchmarkStrategy:
    name: str
    mode: str = "io"
    batch: bool = False
    dedup: bool = True
    workers: int | None = None
    strategy: str = "concurrent"
