# 🧠 RPG Narrative Server — C4 Model (Context / Container / Component)

---

# 🌍 1. CONTEXT DIAGRAM

```mermaid
flowchart TB
    User[Player / GM] --> API[API / Discord Interface]
    API --> App[RPG Narrative Server]

    App --> LLM[LLM Providers]
    App --> VectorIndex[Vector Index]
    App --> Storage[(Storage System)]

    Storage --> JSON[JSON Files]
    Storage --> Memory[In-Memory]
    Storage --> Chroma[ChromaDB]
```

---

# 🧱 2. CONTAINER DIAGRAM

```mermaid
flowchart TB
    subgraph RPG Narrative Server
        API[FastAPI / Discord Adapter]
        Application[Application Layer]
        Domain[Domain Layer]
        Infra[Infrastructure Layer]
    end

    API --> Application
    Application --> Domain
    Application --> Infra

    Infra --> Storage[(Storage)]
    Infra --> VectorIndex[Vector Index]
    Infra --> LLM[LLM Providers]
```

---

# 🧩 3. COMPONENT DIAGRAM (STORAGE)

```mermaid
flowchart LR
    subgraph Application
        Repo[Repositories]
    end

    subgraph Infrastructure
        Adapter[Adapters]
        Backend[Backends]
        KV[KV Store]
        Vector[Vector Store]
    end

    Repo --> Adapter
    Adapter --> Backend
    Backend --> KV
    Backend --> Vector
```

---

# 🧬 4. COMPONENT DIAGRAM (RAG PIPELINE)

```mermaid
flowchart LR
    Input[User Input] --> Embed[Embedding]
    Embed --> Search[Vector Search]
    Search --> Rank[Ranking]
    Rank --> Context[Context Builder]
    Context --> LLM[LLM]
    LLM --> Output[Response]
    Output --> Memory[Memory Persist]
```

---

# 🔥 Key Insights

- Context: system interacts with external LLM + storage
- Containers: clean separation (API / Application / Domain / Infra)
- Components: adapters isolate storage + vector complexity
- RAG: fully modular pipeline

---

# 🚀 Mental Model

```
[User]
   ↓
[API]
   ↓
[Application]
   ↓
[Domain]
   ↓
[Infrastructure]
   ↓
[Storage + Vector + LLM]
```

---

