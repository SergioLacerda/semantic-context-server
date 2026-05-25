"""
Performance benchmarking and SLO validation tests.

Tests validate that the system meets defined performance SLOs from:
/docs/ia/CANONICAL/specifications/performance.md
"""

import statistics
import time
from collections.abc import Callable

import pytest


class PerformanceSLOValidator:
    """Validator for performance SLOs."""

    # Performance budgets in milliseconds (from performance.md)
    LAYER_BUDGETS = {
        "adapter": {"p50": 5, "p99": 10},  # Port/Adapter
        "interface": {"p50": 10, "p99": 20},  # Interfaces/HTTP
        "application": {"p50": 50, "p99": 100},  # UseCase
        "domain": {"p50": 100, "p99": 200},  # Business logic
        "infrastructure": {"p50": 200, "p99": 500},  # DB/External
        "vector": {"p50": 150, "p99": 300},  # Vector search
        "bootstrap": {"p50": 1000, "p99": 2000},  # Startup
        "framework": {"p50": 20, "p99": 50},  # Event bus
    }

    # Throughput minimums (requests per second)
    THROUGHPUT_MINIMUMS = {
        "get_endpoints": 100,
        "post_endpoints": 50,
        "ai_generation": 5,
        "vector_search": 50,
    }

    # Resource limits
    RESOURCE_LIMITS = {
        "memory_per_campaign_mb": 512,
        "memory_per_request_mb": 50,
        "cpu_time_ms": 100,
        "ai_cpu_time_s": 5,
        "storage_per_project_gb": 10,
    }

    @staticmethod
    def measure_latency(func: Callable, iterations: int = 1000) -> dict:
        """
        Measure function latency over multiple iterations.

        Returns dict with latency percentiles and statistics.
        """
        latencies_ms: list[float] = []

        for _ in range(iterations):
            start = time.perf_counter()
            try:
                func()
            except Exception:
                # Record error but continue measurement
                pass
            elapsed = time.perf_counter() - start
            latencies_ms.append(elapsed * 1000)  # Convert to ms

        if not latencies_ms:
            raise RuntimeError("No successful measurements")

        latencies_ms.sort()

        return {
            "p50": statistics.quantiles(latencies_ms, n=100)[49],  # 50th percentile
            "p95": statistics.quantiles(latencies_ms, n=100)[94],  # 95th percentile
            "p99": statistics.quantiles(latencies_ms, n=100)[98],  # 99th percentile
            "min": min(latencies_ms),
            "max": max(latencies_ms),
            "mean": statistics.mean(latencies_ms),
            "stdev": statistics.stdev(latencies_ms) if len(latencies_ms) > 1 else 0,
            "samples": len(latencies_ms),
        }

    @staticmethod
    def measure_throughput(func: Callable, duration_seconds: float = 10) -> dict:
        """
        Measure function throughput (operations per second).

        Runs function for specified duration and counts completions.
        """
        count = 0
        start = time.perf_counter()

        while time.perf_counter() - start < duration_seconds:
            try:
                func()
                count += 1
            except Exception:
                # Continue counting even if errors occur
                pass

        elapsed = time.perf_counter() - start

        return {
            "operations": count,
            "duration_seconds": elapsed,
            "ops_per_second": count / elapsed,
            "min_rps": count / elapsed,  # Measured RPS
        }

    @classmethod
    def validate_latency_slo(cls, layer: str, measured_p99: float) -> tuple[bool, str]:
        """
        Validate measured latency against SLO for layer.

        Returns (passed: bool, message: str)
        """
        if layer not in cls.LAYER_BUDGETS:
            return False, f"Unknown layer: {layer}"

        budget = cls.LAYER_BUDGETS[layer]
        p99_limit = budget["p99"]

        if measured_p99 <= p99_limit:
            return True, f"✅ {layer} P99: {measured_p99:.1f}ms (limit: {p99_limit}ms)"
        else:
            margin = ((measured_p99 - p99_limit) / p99_limit) * 100
            return (
                False,
                f"❌ {layer} P99: {measured_p99:.1f}ms "
                f"(limit: {p99_limit}ms, {margin:.0f}% over budget)",
            )

    @classmethod
    def validate_throughput_slo(cls, endpoint: str, measured_rps: float) -> tuple[bool, str]:
        """
        Validate measured throughput against SLO for endpoint.

        Returns (passed: bool, message: str)
        """
        if endpoint not in cls.THROUGHPUT_MINIMUMS:
            return False, f"Unknown endpoint: {endpoint}"

        minimum_rps = cls.THROUGHPUT_MINIMUMS[endpoint]

        if measured_rps >= minimum_rps:
            return True, f"✅ {endpoint}: {measured_rps:.1f} RPS (min: {minimum_rps})"
        else:
            margin = ((minimum_rps - measured_rps) / minimum_rps) * 100
            return (
                False,
                f"❌ {endpoint}: {measured_rps:.1f} RPS "
                f"(min: {minimum_rps}, {margin:.0f}% below budget)",
            )


# Pytest fixtures


@pytest.fixture
def slo_validator():
    """Provide SLO validator instance."""
    return PerformanceSLOValidator()


# Example tests (teams implement project-specific ones)


def test_example_adapter_layer_latency(slo_validator):
    """Example: Adapter layer must meet latency SLO."""

    # Mock function (replace with actual adapter code)
    def adapter_operation():
        # Simulate 2ms operation
        time.sleep(0.002)

    latencies = slo_validator.measure_latency(adapter_operation, iterations=100)

    passed, message = slo_validator.validate_latency_slo("adapter", latencies["p99"])

    print(f"\n{message}")
    print(
        f"  Measured: P50={latencies['p50']:.1f}ms, "
        f"P99={latencies['p99']:.1f}ms, "
        f"Max={latencies['max']:.1f}ms"
    )

    assert passed, message


def test_example_application_layer_latency(slo_validator):
    """Example: Application layer must meet latency SLO."""

    # Mock function (replace with actual usecase code)
    def application_operation():
        # Simulate 40ms operation
        time.sleep(0.040)

    latencies = slo_validator.measure_latency(application_operation, iterations=100)

    passed, message = slo_validator.validate_latency_slo("application", latencies["p99"])

    print(f"\n{message}")
    print(
        f"  Measured: P50={latencies['p50']:.1f}ms, "
        f"P99={latencies['p99']:.1f}ms, "
        f"Max={latencies['max']:.1f}ms"
    )

    assert passed, message


def test_example_get_endpoint_throughput(slo_validator):
    """Example: GET endpoints must meet throughput SLO."""

    # Mock function (replace with actual endpoint)
    def get_operation():
        # Simulate ~9ms operation to keep headroom above 100 RPS on CI.
        time.sleep(0.009)

    throughput = slo_validator.measure_throughput(get_operation, duration_seconds=5)

    passed, message = slo_validator.validate_throughput_slo(
        "get_endpoints", throughput["ops_per_second"]
    )

    print(f"\n{message}")
    print(
        f"  Measured: {throughput['operations']} operations in "
        f"{throughput['duration_seconds']:.1f}s"
    )

    assert passed, message


def test_performance_slo_configuration():
    """Test that SLO configuration is accessible and valid."""
    validator = PerformanceSLOValidator()

    # All layers must have P50 and P99 budgets
    for layer, budgets in validator.LAYER_BUDGETS.items():
        assert "p50" in budgets, f"Layer {layer} missing p50 budget"
        assert "p99" in budgets, f"Layer {layer} missing p99 budget"
        assert budgets["p50"] > 0, f"Layer {layer} p50 must be > 0"
        assert budgets["p99"] > budgets["p50"], f"Layer {layer} p99 must be > p50"

    # All endpoints must have throughput minimum
    for endpoint, rps in validator.THROUGHPUT_MINIMUMS.items():
        assert rps > 0, f"Endpoint {endpoint} RPS must be > 0"

    # All resources must have limits
    for resource, limit in validator.RESOURCE_LIMITS.items():
        assert limit > 0, f"Resource {resource} limit must be > 0"

    print("\n✅ All SLO configurations valid")


# Benchmark report example


def test_generate_performance_report(slo_validator):
    """Generate performance report showing all SLOs."""
    report = "📊 PERFORMANCE SLO REPORT\n"
    report += "=" * 50 + "\n\n"

    report += "📈 Layer Budgets (P99 latency):\n"
    for layer, budgets in slo_validator.LAYER_BUDGETS.items():
        report += f"  {layer:15} P50: {budgets['p50']:5.0f}ms  P99: {budgets['p99']:5.0f}ms\n"

    report += "\n📊 Throughput Minimums (RPS):\n"
    for endpoint, rps in slo_validator.THROUGHPUT_MINIMUMS.items():
        report += f"  {endpoint:20} {rps:3.0f} RPS\n"

    report += "\n💾 Resource Limits:\n"
    for resource, limit in slo_validator.RESOURCE_LIMITS.items():
        unit = "MB" if "mb" in resource else ("GB" if "gb" in resource else "ms/s")
        report += f"  {resource:25} {limit:8.0f} {unit}\n"

    report += "\n" + "=" * 50
    print(report)
