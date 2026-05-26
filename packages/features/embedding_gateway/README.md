# packages/features/embedding_gateway

Embedding provider orchestration — contracts, services, providers, and registry.

Status: extracted

## Structure

| Module | Exports |
|--------|---------|
| `contracts` | `EmbeddingGatewayContract`, `EmbeddingProviderContract` |
| `service` | `EmbeddingGatewayService` (dict-based multi-provider), `EmbeddingService` (resilience-aware) |
| `registry` | `EmbeddingRegistry` |
| `fallback` | `deterministic_vector`, `VectorSpace` |
| `providers/gemini` | `GeminiEmbeddingProvider` |
| `providers/openai` | `OpenAIEmbeddingProvider` |
| `providers/ollama` | `OllamaEmbeddingProvider` |
| `providers/lmstudio` | `LMStudioEmbeddingProvider` |
| `providers/sentence` | `SentenceEmbeddingProvider` |

## Deferred

- `infrastructure/embeddings/factory.py::create_embedding` → app-layer wiring, re-entry via apps/narrative_server card
- `application/services/embedding_strategy.py::EmbeddingStrategy` → usecase orchestration, re-entry via rpg_engine card
