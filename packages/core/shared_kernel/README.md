# packages/core/shared_kernel

Cross-cutting utilities shared across all packages. No domain knowledge, no external dependencies beyond the standard library.

Status: extracted

## Modules

| Module | Exports |
|--------|---------|
| `hash_utils` | `normalize_text`, `stable_sha256`, `sha256_hash` |
| `text_io` | `read_text_utf8`, `write_text_utf8`, `append_text_utf8` |
| `json_utils` | `load_json`, `save_json`, `update_json` |
| `execution` | `on_executor` |
| `resilience` | `resilient_call` |
| `logging_context` | `request_id_var`, `set_request_id`, `get_request_id` |

## Deferred

- `logging/config.py::setup_logging` → app-layer concern, migrated with apps/narrative_server card
- `cache/cache.py::CacheManager` → belongs to features/semantic_cache package card
