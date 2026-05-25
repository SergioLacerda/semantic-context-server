# 🔎 RAG Pipeline — Definitivo (PT-BR)

## 🎯 Visão Geral

O pipeline de RAG (Retrieval-Augmented Generation) do RPG Narrative Server é multi-stage e orientado a contexto narrativo.

---

## 🟢 Visão Simplificada

```mermaid
flowchart TD
A[Input] --> B[Hybrid Retrieval]
B --> C[Ranking]
C --> D[Context Builder]
D --> E[LLM]
E --> F[Memory Update]
```

---

## 🔵 Pipeline Completo

```mermaid
flowchart TD

A[Input]
--> B[Normalizer]

B --> C[Classifier]
C --> D[Intent Detection]
C --> E[Context Type]

D --> F[Query Planner]
E --> F

F --> G[Strategy Selector]

G --> H1[Vector Search]
G --> H2[Keyword Search]
G --> H3[Graph Traversal]
G --> H4[Timeline Index]

H1 --> I[Merge]
H2 --> I
H3 --> I
H4 --> I

I --> J[Stage 1 Rank]
J --> K[Stage 2 Rank]
K --> L[Final Rank]

L --> M[Deduplication]
M --> N[Token Filter]

N --> O[Context Builder]
O --> P[Memory Injection]

P --> Q[Prompt Builder]
Q --> R[LLM Call]

R --> S[Post Processing]
S --> T[Event Dispatch]

T --> U[Episodic Memory]
T --> V[Vector Index Update]
T --> W[Narrative Graph]
```

---

## 🧪 Exemplo

### Input

"atacar o goblin"

### Contexto recuperado

- estado do jogador
- histórico de combate

### Output

"Você avança com sua espada..."

---

## 🧠 Estratégias

- Retrieval híbrido (vector + keyword + graph + timeline)
- Ranking multi-stage
- Controle de tokens
- Deduplicação

---

## 🧰 Debug

- validar contexto gerado
- inspecionar ranking
- analisar prompt final

---

## ⚙️ Extensibilidade

- adicionar novo provider de retrieval
- alterar estratégia no planner
- ajustar ranking
