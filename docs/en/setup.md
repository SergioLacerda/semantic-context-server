# ⚙️ Setup Guide — RPG Narrative Server (EN)

This guide covers **full environment setup**, including virtual environment, dependencies, profiles, and how to run the server.

---

## 🐍 1. Create Virtual Environment

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

## 📦 2. Install Dependencies

### Default (minimal)

```bash
pip install -e .
```

### Development (recommended)

```bash
pip install -e .[dev]
```

### Full (LLM + embeddings + vector DB)

```bash
pip install -e .[full]
```

### Combined

```bash
pip install -e .[dev,full]
```

---

### ⚡ Alternative (uv)

```bash
uv sync --all-extras
```

---

### 🧠 Profiles Explained

```text
| Profile | Description |
|--------|-------------|
| dev | testing, linting, tooling |
| full | all providers (LLM, embeddings, vector DB) |
| default | minimal runtime |
```

---

## ⚙️ 3. Environment Variables

```bash
cp .env.example .env
```

Example:

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
DEVICE=cpu

CHROMA_PERSIST_DIR=./data/chroma
```

---

## ▶️ 4. Running the Server

### CLI

```bash
semantic_context_server
```

### FastAPI

```bash
uvicorn rpg_narrative_server.app:app --reload --port 8000
```

### Using uv

```bash
uv run rpg_narrative_server
```

---

## 🤖 5. Discord Adapter

```bash
python interfaces/discord/main.py
```

---

## 📚 6. API Docs

Open:

```bash
http://localhost:8000/docs
```

---

## 🧪 7. Run Tests

```bash
pytest -n auto --dist=loadscope --cov=src/rpg_narrative_server --cov-report=term-missing
```

---

## 🧹 8. Clear Cache (optional)

```bash
find . -name "__pycache__" -exec rm -r {} +
find . -name "*.pyc" -delete
```

---
