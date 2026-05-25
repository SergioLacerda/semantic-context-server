# 🚀 Retrieval Engine Benchmark

Official tool for performance analysis of the Retrieval (RAG) pipeline.

------------------------------------------------------------------------

## 🧠 Purpose

Evaluate system behavior under different conditions:

-   Latency (avg / p95 / p99)
-   Throughput (req/s)
-   Concurrency scalability
-   CPU vs IO impact
-   Deduplication efficiency
-   Batching benefits

------------------------------------------------------------------------

## ▶️ Execution

``` bash
python scripts/benchmark/run.py --compare
```

> ⚠️ Run from project root

------------------------------------------------------------------------

## ⚙️ Parameters

  Flag           Description
  -------------- ---------------------------------------
  `--n`          Number of requests (default: 50)
  `--mode`       Workload type (`io`, `cpu`, `jitter`)
  `--compare`    Run all modes automatically
  `--no-dedup`   Disable deduplication
  `--batch`      Enable embedding batching
  `--workers`    Number of executor workers
  `--cpu-work`   CPU workload intensity

------------------------------------------------------------------------

## 🔥 Execution Modes

### 🧊 IO-bound (default)

``` bash
python scripts/benchmark/run.py --mode io
```

------------------------------------------------------------------------

### 🌐 Jitter (realistic scenario)

``` bash
python scripts/benchmark/run.py --mode jitter
```

------------------------------------------------------------------------

### 🧠 CPU-bound

``` bash
python scripts/benchmark/run.py --mode cpu
```

------------------------------------------------------------------------

### 🔄 Full comparison

``` bash
python scripts/benchmark/run.py --compare
```

------------------------------------------------------------------------

## 📊 Metrics

  Metric       Description
  ------------ -------------------------
  throughput   requests per second
  avg          average latency
  p95          95th percentile latency
  p99          tail latency
  total_time   total execution time
  calls        actual index calls

------------------------------------------------------------------------

## 🧠 Interpretation

  Scenario    Expected behavior
  ----------- --------------------------
  IO-bound    Scales well with threads
  CPU-bound   Better with process
  Jitter      Increases p95/p99
  Dedup ON    Reduces calls
  Batch ON    Improves throughput

------------------------------------------------------------------------

## 📌 Best Practices

-   Run benchmarks in isolation
-   Compare multiple executions
-   Use `--compare` for baseline
-   Monitor regressions after RAG changes

------------------------------------------------------------------------

## 🚀 Future Improvements

-   JSON export (for dashboards)
-   CI integration (performance regression)
-   Visualization (charts)
-   Profiling (CPU/memory)

------------------------------------------------------------------------

## 💡 Tips

-   Use `jitter` to simulate production
-   Combine `batch + dedup` for best gains
-   Use `cpu` to test parallelism limits
