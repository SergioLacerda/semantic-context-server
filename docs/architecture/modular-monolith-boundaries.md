# Modular Monolith Boundaries

> **Authoritative reference**: [ADR-001 — Migration from Flat Monolith to Modular Monorepo with Composable Autonomy](decisions/ADR-001-modular-monorepo-migration.md)
>
> This document is a summary. For full rationale, alternatives considered, and migration strategy, see ADR-001.

---

This document defines the boundary contract for the semantic-context-server package architecture.

## Package Hierarchy

```
apps → interfaces → prompt_engines → features → shared_kernel
```

- `packages/core/shared_kernel` — cross-cutting utilities (hash, text I/O, JSON, logging context, resilience, execution). No domain logic.
- `packages/features/prompt_engine_*` — orchestration layer; own full and summarized flows across autonomous features
- `packages/features/*` — autonomous feature packages with internal Clean Architecture layers
- `packages/interfaces/*` — delivery adapters (HTTP, Discord); route through `prompt_engine_*` for orchestrated flows
- `apps/*` — application entry points; zero business logic

## Boundary Rules

1. Feature packages must not import from each other directly.
2. All cross-feature communication must go through Ports (`application/ports/` — Python Protocol types).
3. `shared_kernel` is importable by all layers but must never import from `features/` or `interfaces/`.
4. `apps/` and `interfaces/` must not call feature packages directly for orchestrated flows — they go through `prompt_engine_*`.
5. Application ports not yet migrated remain in `src/semantic_context_server/application/ports/` until `src/` is deleted.

## Migration Status

`src/semantic_context_server/` coexists with `packages/` during migration. `src/` is treated as read-only; all new code goes to `packages/`. `src/` is deleted when all features are migrated and the test suite passes on new import paths.

See ADR-001 for the full migration strategy.
