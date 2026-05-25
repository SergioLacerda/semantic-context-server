# ⚙️ Guia de Setup — RPG Narrative Server (PT-BR)

Este guia cobre o **setup completo do ambiente**, incluindo ambiente virtual, instalação com profiles, configuração e execução do servidor.

---

## 🐍 1. Criar ambiente virtual (venv)

### Linux / Mac

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Windows (PowerShell)

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

---

## 📦 2. Instalar dependências

## 🔹 Instalação padrão (mínima)

```bash
pip install -e .
```

### 🧪 Desenvolvimento (recomendado)

```bash
pip install -e .[dev]
```

### 🚀 Completo (LLM + embeddings + vector DB)

```bash
pip install -e .[full]
```

### ⚡ Perfis combinados

```bash
pip install -e .[dev,full]
```

---

## ⚡ Alternativa com uv

```bash
uv sync --all-extras
```

---

## 🧠 Profiles (explicação)

```text
| Profile | Descrição |
|--------|----------|
| dev | testes, lint e ferramentas de desenvolvimento |
| full | todos providers (LLM, embeddings, vector DB) |
| default | instalação mínima |
```

---

## ⚙️ 3. Variáveis de ambiente

```bash
cp .env.example .env
```

Exemplo:

```bash
ENVIRONMENT=development

DISCORD_ENABLE=true # opcional, default: true
DISCORD_PUBLIC_KEY=...
DISCORD_APPLICATION_ID=...
DISCORD_TOKEN=...

LLM_PROVIDER=openai
LLM_MODEL=gpt-4o-mini
OPENAI_API_KEY=...

EMBEDDING_PROFILE=local
EMBEDDING_PROVIDER=sentence-transformers
DEVICE=cpu  # ou cuda

CHROMA_PERSIST_DIR=./data/chroma
```

---

## ▶️ 4. Executar o servidor

### CLI

```bash
semantic_context_server
```

### API (FastAPI)

```bash
uvicorn rpg_narrative_server.app:app --reload --port 8000
```

### Usando uv

```bash
uv run rpg_narrative_server
```

---

@# 🤖 5. Adapter Discord

```bash
python interfaces/discord/main.py
```

---

## 📚 6. Documentação da API

Acesse:

```bash
http://localhost:8000/docs
```

---

## 🧪 7. Rodar testes

```bash
pytest
```

---

## 🧹 8. Limpeza de cache (opcional)

```bash
find . -name "__pycache__" -exec rm -r {} +
find . -name "*.pyc" -delete
```

---
