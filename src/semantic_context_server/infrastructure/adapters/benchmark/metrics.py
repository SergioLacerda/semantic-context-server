import statistics
from typing import Any


def percentile(data: Any, p: Any) -> Any:
    if not data:
        return 0.0

    data = sorted(data)
    k = (len(data) - 1) * (p / 100)
    f = int(k)
    c = min(f + 1, len(data) - 1)

    if f == c:
        return data[int(k)]

    return data[f] + (data[c] - data[f]) * (k - f)


def build_report(latencies: Any, total_time: Any, calls: Any) -> Any:
    if not latencies:
        return {
            "requests": 0,
            "total_time": total_time,
            "throughput": 0,
            "avg": 0,
            "p95": 0,
            "p99": 0,
            "calls": calls,
        }

    avg = statistics.mean(latencies)
    p95 = percentile(latencies, 95)
    p99 = percentile(latencies, 99)

    throughput = len(latencies) / total_time if total_time > 0 else 0

    return {
        "requests": len(latencies),
        "total_time": total_time,
        "throughput": throughput,
        "avg": avg,
        "p95": p95,
        "p99": p99,
        "calls": calls,
    }


def print_report(report: Any) -> None:
    print("\n--- REPORT ---")
    for k, v in report.items():
        print(f"{k}: {v:.4f}" if isinstance(v, float) else f"{k}: {v}")
