# 🧠 RPG Narrative Server

![Python](https://img.shields.io/badge/python-3.12-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Architecture](https://img.shields.io/badge/architecture-clean--hexagonal-orange)
![RAG](https://img.shields.io/badge/RAG-multi--stage-purple)
![Status](https://img.shields.io/badge/status-active-success)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-teal)
![Discord](https://img.shields.io/badge/Discord-Interactions-blue)
![Tests](https://img.shields.io/badge/tests-pytest-informational)
[![CI](https://github.com/SergioLacerda/semantic-context-server/actions/workflows/ci.yml/badge.svg)](https://github.com/SergioLacerda/semantic-context-server/actions/workflows/ci.yml)
[![Codecov](https://codecov.io/gh/SergioLacerda/semantic-context-server/graph/badge.svg)](https://codecov.io/gh/SergioLacerda/semantic-context-server)
---

## 🚀 Narrative Engine for RPG Storytelling

RPG Narrative Server is a **modular narrative engine** powered by:

- 🧠 LLM (OpenAI or local)
- 🔎 Advanced RAG pipeline
- 💾 Persistent campaign memory
- 🔌 Multiple interfaces (Discord, API, CLI)

> This is **not a bot** — it is a **narrative server platform**.

---

## 🌍 Documentation

### 🇧🇷 Português

- 📚 [docs/pt-br/README.md](docs/pt-br/README.md)
- ⚙️ [docs/pt-br/setup.md](docs/pt-br/setup.md)
- 🧠 [docs/pt-br/architecture.md](docs/pt-br/architecture.md)
- 🔎 [docs/pt-br/rag_pipeline.md](docs/pt-br/rag_pipeline.md)
- 📊 [docs/pt-br/benchmark.md](docs/pt-br/benchmark.md)

### 🇺🇸 English

- 📚 [docs/en/README.md](docs/en/README.md)
- ⚙️ [docs/en/setup.md](docs/en/setup.md)
- 🧠 [docs/en/architecture.md](docs/en/architecture.md)
- 🔎 [docs/en/rag_pipeline.md](docs/en/rag_pipeline.md)
- 📊 [docs/en/benchmark.md](docs/en/benchmark.md)

---

## 🚀 Quick Start

Requires [uv](https://docs.astral.sh/uv/) and `make`.

```bash
git clone https://github.com/SergioLacerda/semantic-context-server.git
cd semantic-context-server

cp .env.example .env

make sync   # install dev + test dependencies
make run    # start the server
```

👉 Open API docs: `http://localhost:8000/docs`

No manual virtualenv activation needed — `uv` manages the environment.

---

## 🧠 Core Concepts

### 🔹 Clean Architecture

- Domain is isolated
- UseCases define behavior
- Infrastructure is replaceable

### 🔹 RAG Pipeline

- Hybrid retrieval (vector + keyword + graph + timeline)
- Multi-stage ranking
- Context-aware generation

### 🔹 Narrative Engine

- Persistent memory
- Event-driven updates
- Multi-session campaigns

---

## 🛠 Developer Workflow

All commands run through `make` — no direct `pytest`, `ruff`, or `mypy` calls needed.

| Command | What it does |
|---|---|
| `make sync` | Install dev + test dependencies |
| `make sync-ci` | Install CI dependencies (frozen lock) |
| `make run` | Start uvicorn server |
| `make test` | Run all tests |
| `make test-fast` | Run fast tests only (skip slow + integration) |
| `make lint` | Unified quality gate (ruff + mypy + architecture + contract) |
| `make fmt` | Auto-fix available lint issues and re-run lint gate |
| `make type` | Run mypy |
| `make arch` | Run architecture validation tests |
| `make contract` | Run contract tests |
| `make ci` | Full local CI pipeline (lint → type → arch → contract → test) |
| `make lock` | Regenerate `uv.lock` |
| `make lock-check` | Assert lock is consistent |
| `make clean` | Remove caches |

### Pre-commit hooks

```bash
make hooks-install
```

---

## 📊 Benchmark

Use the CLI entrypoint:

```bash
uv run server-benchmark --help
```

---

## 🤝 Contributing

**Framework:** This project follows the [SDD Architecture Framework](https://github.com/SergioLacerda/sdd-architecture) (`sdd-architecture`) for governance and development discipline.

Before contributing, read the architecture governance:

- 📖 [Architecture Specification](docs/ia/specs/_shared/architecture.md) — Mandatory design patterns
- 🧪 [Testing Best Practices](docs/ia/specs/_shared/testing.md) — Testing strategies
- ⚖️ [AI Rules](docs/ia/ai-rules.md) — Execution protocols for AI agents
- 🏛️ [Constitution](docs/ia/specs/constitution.md) — Non-negotiable principles

**Requirements:**
- Clean Architecture + Ports & Adapters (mandatory)
- All I/O must be async
- No test-specific code in production
- Vector index treated as black box
- Do not couple infra into domain
- Use ports for integrations
- Avoid overengineering

---

## 📌 Status

- 🚧 Active development
- 🔧 Stabilization phase
- 🧠 RAG evolving

---

## 🚀 Vision

A platform for:

- dynamic storytelling
- AI-driven RPG campaigns
- extensible narrative systems
