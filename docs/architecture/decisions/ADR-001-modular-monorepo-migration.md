# ADR-001: Migration from Flat Monolith to Modular Monorepo with Composable Autonomy

| Field      | Value                          |
|------------|--------------------------------|
| Status     | Accepted                       |
| Date       | 2026-05-26                     |
| Deciders   | Sergio Lacerda                 |
| Supersedes | —                              |

---

## Context

The project originated as a single-purpose RPG narrative server implemented as one Python package under `src/semantic_context_server/`, following Clean Architecture (domain → application → infrastructure → interfaces → frameworks). As the system evolves into a **multi-domain semantic compression engine** — supporting RPG storytelling, developer tooling, Discord bot, REST API, and multiple LLM integrations — the flat namespace creates structural problems:

- Features cannot be tested in isolation
- Dependency direction is enforced only by convention, not by tooling
- Adding new delivery surfaces (API, Discord, new LLMs) inflates the same namespace
- Partial stacks (e.g., semantic compression without RPG logic) cannot be wired cleanly

A migration is underway: `packages/` and `apps/` directories are being built alongside `src/`. The `src/` tree remains as a reference during migration and is **deleted** when migration is complete.

---

## Decision

Adopt a **modular monorepo** layout within a single deployable Python application, governed by the principle of **Composable Autonomy**: every feature package is an autonomous unit that communicates exclusively via published Ports (Python Protocol types).

---

## Package Hierarchy

```
semantic-context-server/
│
├── apps/
│   └── narrative_server/          ← entry points only, zero business logic
│
├── packages/
│   ├── core/
│   │   └── shared_kernel/         ← cross-cutting utilities (see rules below)
│   │
│   ├── features/
│   │   ├── prompt_engine_core/    ← shared compression primitives
│   │   ├── prompt_engine_rpg/     ← orchestrates RPG flows (full + summarized)
│   │   ├── llm_gateway/           ← autonomous: LLM integration
│   │   ├── vector_index/          ← autonomous: semantic search & retrieval
│   │   ├── rpg_engine/            ← autonomous: RPG domain logic
│   │   ├── embedding_gateway/     ← autonomous: text → vector
│   │   ├── semantic_cache/        ← autonomous: semantic cache layer
│   │   └── benchmark_engine/      ← autonomous: performance validation
│   │
│   └── interfaces/
│       ├── discord_bot/           ← Discord delivery adapter
│       └── http_api/              ← REST API delivery adapter
│
└── pyproject.toml                 ← single build file for the entire monorepo
```

**Dependency direction (strict, no exceptions):**

```
apps  →  interfaces  →  prompt_engines  →  features  →  shared_kernel
```

No layer may import from a layer above it.

---

## Boundary Rules

### 1. Features communicate only via Contracts

Each feature package exposes its public contract in a `contracts.py` module at the package root, using Python Protocol types. All consumers — including orchestrators — import only from `contracts.py`.

```python
# ALLOWED — importing the contract (Protocol) for dependency injection
from packages.features.llm_gateway.contracts import LLMGatewayContract
from packages.features.embedding_gateway.contracts import EmbeddingGatewayContract

# FORBIDDEN — bypasses the contract boundary
from packages.features.llm_gateway.service import LLMGatewayService
from packages.features.llm_gateway.infrastructure.openai_adapter import OpenAIAdapter
```

### 2. Cross-feature imports are limited to contracts

A module inside `packages/features/<name>/` may only import from another feature's `contracts.py` — never from its `service.py`, `domain/`, or `infrastructure/`. Cross-feature wiring of concrete implementations happens at the orchestration layer (`prompt_engine_*`) or at the app entry point via dependency injection.

### 3. shared_kernel has hard boundaries

`shared_kernel` **may contain**: hash utilities, JSON utilities, logging context, resilience primitives, text I/O helpers, execution utilities, environment config, user profile primitives.

`shared_kernel` **must never contain**: domain entities, feature-specific DTOs, business rules, or anything that imports from `packages/features/*` or `packages/interfaces/*`.

### 4. Apps are thin entry points

`apps/` modules wire dependencies and start processes. They never contain business logic. All orchestrated flows are initiated through a `prompt_engine_*` Port.

---

## Orchestration Model

Centralized `application/usecases/` (legacy pattern from `src/`) is replaced by domain-scoped **prompt engine** packages:

| Package | Responsibility |
|---|---|
| `prompt_engine_rpg` | Orchestrates RPG flows: **full** (raw input → rpg_engine → vector_index → llm_gateway → response) and **summarized** (input → vector_index → semantic_cache → compressed context, no LLM) |
| `prompt_engine_core` | Shared tokenization and compression primitives used by all `prompt_engine_*` packages |
| *(future)* `prompt_engine_dev` | Developer tooling flows |

This enables **partial delivery stacks**: an HTTP API can wire only `vector_index` + `semantic_cache` for semantic compression without pulling in any RPG logic.

### CQRS

CQRS (separate `commands/` and `queries/` under `application/`) is **not mandated globally**. A feature adopts it when its read/write models diverge structurally or have different consistency requirements. Simple features (e.g., `embedding_gateway`) use a flat use-case structure.

---

## Migration Strategy

1. **All new code** goes into `packages/`, never into `src/`
2. Modules are moved from `src/` to `packages/` incrementally, feature by feature
3. Each migration unit (feature + its tests) is self-contained — tests are updated in the same step as the move
4. `import-linter` contracts are updated in the same PR as the feature move; CI fails if contracts are stale
5. **Completion criterion**: `src/` is deleted when all modules have counterparts in `packages/` and the full test suite passes against new import paths
6. No compatibility shims, no `__init__.py` re-exports bridging `src/` to `packages/`

---

## Consequences

**Positive:**
- Each feature can be understood, tested, and evolved independently
- `import-linter` can enforce Clean Architecture per feature boundary
- Partial delivery stacks (semantic compression API, full RPG bot) are first-class supported
- Dependency direction is enforced by tooling, not convention

**Negative / Risks:**
- `src/` and `packages/` coexist during migration — treat `src/` as read-only
- Import paths change across the codebase; test churn is expected
- `import-linter` contracts require maintenance as features are added

**Guardrails:**
- Test suite is the primary regression shield — green tests gate every migration step
- `import-linter` catches cyclic imports and layer violations in CI
- Code review challenges any addition to `shared_kernel` that has domain semantics (those belong in `prompt_engine_core`)
- `prompt_engine_rpg` is refactored if it exceeds ~5 orchestrated flows or ~8 handlers per command/query directory

---

## Alternatives Considered

| Alternative | Reason Rejected |
|---|---|
| Centralized orchestration in `apps/` | Apps become business logic holders, violating Clean Architecture |
| Microservices / separate deployables | Distributed complexity unwarranted for current scale; single deployable suffices |
| Abstract base classes instead of Protocols | ABCs couple consumers to the definition site; Protocols are structurally typed |
| Shared DTOs in `shared_kernel` | DTOs belong to the feature that owns the concept; `shared_kernel` must not know about feature semantics |
| Parallel `src/` maintenance (deprecation shims) | Doubles the maintenance surface; clean deletion is faster and safer |

---

## Related Documents

- [Modular Monolith Boundaries](../modular-monolith-boundaries.md) — package boundary contract (references this ADR)
- [OpenSpec Change](../../../openspec/changes/adr-modular-monorepo-migration/) — design rationale and implementation tasks
