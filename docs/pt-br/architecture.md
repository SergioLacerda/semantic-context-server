# 🧠 Arquitetura (Engine-Level)

## 🎯 Visão

O RPG Narrative Server é um **servidor de narrativa desacoplado**, baseado em Clean Architecture.

---

## 🧱 Camadas

```mermaid
flowchart LR
A[Interfaces] --> B[Application]
B --> C[Domain]
B --> D[Ports]
D --> E[Infrastructure]
```

---

## 🔄 Fluxo completo

```mermaid
sequenceDiagram
User->>API: Request
API->>UseCase: Execute
UseCase->>Retrieval: Context
UseCase->>LLM: Generate
UseCase->>Memory: Persist
UseCase-->>API: Response
```

---

## 🧠 Decisões arquiteturais

- ❌ Sem frameworks no domain
- ✅ Ports isolam dependências
- ✅ Infra trocável (LLM, DB)

---

## 🔧 Extensibilidade

Para adicionar novo LLM:

1. Criar implementação de LLMPort
2. Registrar no provider
3. Configurar via ENV
