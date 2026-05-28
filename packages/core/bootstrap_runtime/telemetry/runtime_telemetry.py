from __future__ import annotations

import time
from contextlib import contextmanager
from typing import Any

try:
    from opentelemetry import metrics, trace
    from opentelemetry.trace import Status, StatusCode
except ImportError:  # pragma: no cover - optional dependency
    metrics = None
    trace = None
    Status = None
    StatusCode = None


class _NoOpSpan:
    def set_status(self, _status: Any) -> None:
        return None


class _NoOpSpanCM:
    def __enter__(self) -> _NoOpSpan:
        return _NoOpSpan()

    def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        return None


class _NoOpTracer:
    def start_as_current_span(self, _name: str) -> _NoOpSpanCM:
        return _NoOpSpanCM()


class _NoOpMetric:
    def record(self, *_args: Any, **_kwargs: Any) -> None:
        return None

    def add(self, *_args: Any, **_kwargs: Any) -> None:
        return None


class _NoOpMeter:
    def create_histogram(self, _name: str) -> _NoOpMetric:
        return _NoOpMetric()

    def create_counter(self, _name: str) -> _NoOpMetric:
        return _NoOpMetric()

    def create_up_down_counter(self, _name: str) -> _NoOpMetric:
        return _NoOpMetric()


class RuntimeTelemetry:
    def __init__(self) -> None:
        if trace is None or metrics is None:
            self._tracer = _NoOpTracer()
            self._meter = _NoOpMeter()
        else:
            self._tracer = trace.get_tracer("bootstrap_runtime")
            self._meter = metrics.get_meter("bootstrap_runtime")
        self._phase_duration = self._meter.create_histogram("bootstrap.phase.duration_ms")
        self._orphan_count = self._meter.create_counter("executor.orphan_count")
        self._dead_letter_count = self._meter.create_counter("bus.dead_letter_count")
        self._queue_depth = self._meter.create_up_down_counter("executor.queue_depth")

    def record_phase_duration(self, phase: str, status: str, duration_ms: float) -> None:
        self._phase_duration.record(duration_ms, {"phase": phase, "status": status})

    @contextmanager
    def phase_span(self, phase_name: str) -> Any:
        start = time.perf_counter()
        with self._tracer.start_as_current_span(f"bootstrap.{phase_name}") as span:
            try:
                yield span
                duration_ms = (time.perf_counter() - start) * 1000.0
                self.record_phase_duration(phase_name, "ok", duration_ms)
            except Exception:
                if Status is not None and StatusCode is not None:
                    span.set_status(Status(StatusCode.ERROR))
                duration_ms = (time.perf_counter() - start) * 1000.0
                self.record_phase_duration(phase_name, "error", duration_ms)
                raise

    def record_orphan(self) -> None:
        self._orphan_count.add(1)

    def record_dead_letter(self, bus_type: str) -> None:
        self._dead_letter_count.add(1, {"bus_type": bus_type})

    def record_queue_depth(self, domain: str, depth: int) -> None:
        self._queue_depth.add(depth, {"domain": domain})
