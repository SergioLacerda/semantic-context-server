# packages/features/semantic_cache

Cache infrastructure and semantic cache service — base cache, implementations, and managers.

Status: extracted

## Structure

| Module | Exports |
|--------|---------|
| `contracts` | `SemanticCacheContract` |
| `service` | `SemanticCacheService`, `LegacySemanticCacheAdapter` |
| `base_cache` | `AsyncKVAdapter`, `BaseCache` |
| `implementations` | `SemanticCache`, `EmbeddingCache`, `ResponseCache` |
| `cache_manager` | `BaseCacheManager`, `SemanticCacheManager`, `EmbeddingCacheManager`, `ResponseCacheManager` |

## Deferred

- `shared/cache/cache.py::CacheManager` → depends on `config.settings` mutable singleton; re-entry via apps/narrative_server card
