# packages/features/vector_index

Vector index capability package — engine, pipeline, retrieval, ranking, and RAG services.

Status: extracted

## Structure

| Module | Exports |
|--------|---------|
| `contracts` | `VectorStoreContract`, `VectorIndexContract`, `VectorIndexGateway`, `VectorWriterPort`, `VectorReaderPort` |
| `service` | `VectorIndexService` |
| `engine` | `VectorIndex`, `SearchContext`, `PipelineDeps` |
| `components` | `VectorIndexComponents` + internal protocols |
| `adapter` | `VectorIndexAdapter` |
| `builder` | `VectorIndexBuilder` |
| `retrieval_engine` | `RetrievalEngine` |
| `writer` | `VectorWriterService` |
| `reader` | `VectorReaderService` |
| `ann/` | IVFBuilder, IVFRouter, HnswIndex, QdrantANN, FaissANN |
| `classifiers/` | DefaultQueryClassifier |
| `clustering/` | ClusterBuilder, ClusterManager, ClusterRouter, SimpleClusterRouter |
| `narrative/` | CausalityGraph, TimelineIndex |
| `pipeline/` | RetrievalPipeline, PipelineBuilder, all stages |
| `ranking/` | Stage1Ranker, Stage2Ranker, RankingFinal, HybridRanker |
| `runtime/` | InflightDeduplicator, LazySimilarity, RankingContext |
| `utils/` | similarity, topk |
| `providers/` | MemoryProvider |
| `indexing/` | EmbeddingIndexer |

## Deferred

- `vector_index/api/index.py` → HTTP API surface, deferred to interfaces/http-api card
