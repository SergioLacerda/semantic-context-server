# 🚀 Retrieval Engine Benchmark

Ferramenta oficial para análise de performance do pipeline de Retrieval
(RAG).

------------------------------------------------------------------------

## 🧠 Objetivo

Avaliar o comportamento do sistema sob diferentes condições:

- Latência (avg / p95 / p99)
- Throughput (req/s)
- Escalabilidade com concorrência
- Impacto de CPU vs IO
- Eficiência de deduplicação
- Benefícios de batching

------------------------------------------------------------------------

## ▶️ Execução

``` bash
python scripts/benchmark/run.py --compare
```

> ⚠️ Execute a partir da raiz do projeto

------------------------------------------------------------------------

## ⚙️ Parâmetros

```text
  Flag           Descrição
  -------------- ----------------------------------------
  `--n`          Número de requests (default: 50)
  `--mode`       Tipo de carga (`io`, `cpu`, `jitter`)
  `--compare`    Executa todos os modos automaticamente
  `--no-dedup`   Desativa deduplicação
  `--batch`      Ativa batching de embeddings
  `--workers`    Número de workers do executor
  `--cpu-work`   Intensidade de carga CPU
```

------------------------------------------------------------------------

## 🔥 Modos de Execução

### 🧊 IO-bound (default)

``` bash
python scripts/benchmark/run.py --mode io
```

------------------------------------------------------------------------

### 🌐 Jitter

``` bash
python scripts/benchmark/run.py --mode jitter
```

------------------------------------------------------------------------

### 🧠 CPU-bound

``` bash
python scripts/benchmark/run.py --mode cpu
```

------------------------------------------------------------------------

### 🔄 Comparação automática

``` bash
python scripts/benchmark/run.py --compare
```

------------------------------------------------------------------------

## 📊 Métricas

- throughput
- avg
- p95
- p99
- total_time
- calls

------------------------------------------------------------------------

## 📌 Boas práticas

- Rodar isolado
- Comparar execuções
- Monitorar regressões
