# 🧠 RPG Narrative Server — Storage & RAG Architecture Diagram

## 🎯 Overview

This document describes the full storage and retrieval flow using Clean Architecture + Ports & Adapters.

---

## 🧱 High-Level Architecture

```mermaid
flowchart TD
    A[Application Layer] -->|Ports| B[Adapters]
    B --> C[Storage Abstraction]
    C --> D[Backends]
    D --> E[(Physical Storage)]

    subgraph Application
        A1[Use Cases]
        A2[Services]
    end

    subgraph Adapters
        B1[KV Adapter]
        B2[Vector Adapter]
        B3[Document Store]
    end

    subgraph Backends
        D1[JSON Backend]
        D2[InMemory Backend]
        D3[Chroma Backend]
    end
```

---

## 🔁 RAG Flow

```mermaid
sequenceDiagram
    participant User
    participant API
    participant Service
    participant VectorStore
    participant Storage
    participant LLM

    User->>API: Request
    API->>Service: Execute UseCase
    Service->>VectorStore: Search(query embedding)
    VectorStore->>Storage: Fetch candidates
    Storage-->>VectorStore: Documents/Vectors
    VectorStore-->>Service: Relevant context
    Service->>LLM: Build prompt + context
    LLM-->>Service: Response
    Service->>Storage: Persist memory
    Service-->>API: Final response
```

---

## 🧩 Storage Breakdown

```mermaid
flowchart LR
    R[Repository] --> A[Adapter]
    A --> B[Backend]
    B --> S[(Storage)]

    subgraph Types
        KV[KV Store]
        DOC[Document Store]
        VEC[Vector Store]
    end

    A --> KV
    A --> DOC
    A --> VEC
```

---

## 🔑 Concepts

### KV Store
- Key → Value storage
- Base persistence layer
- Used for metadata, tokens, configs

### Vector Store
- Stores embeddings
- Enables semantic search
- Used in RAG pipeline

### Adapters
- Translate domain ↔ storage
- Serialize/deserialize data
- Enforce contracts

### Backends
- Implementation detail
- JSON, Memory, Chroma, etc

### Repositories
- Domain-oriented access
- Campaign, Narrative, Memory

---

## 🔥 Key Design Principles

- Clean Architecture enforced
- Storage fully decoupled
- Vector index treated as black box
- Pluggable backends
- Test-friendly (in-memory support)

---

## 🚀 Mental Model

```
Domain → Repository → Adapter → Backend → Storage
                          ↓
                    Vector Store (RAG)
```

---

## 🧠 Final Insight

This architecture allows:

- Swappable storage engines
- Independent evolution of vector search
- Isolation of domain logic
- Scalable RAG pipeline

