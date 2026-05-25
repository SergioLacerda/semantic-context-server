# -------------------------
# 🏗️ STAGE 1 — BUILDER
# -------------------------
FROM python:3.12-slim AS builder

WORKDIR /build

ARG INSTALL_VECTOR_DB=false

# Toolchain apenas para build
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copia apenas o necessário (melhor cache)
COPY pyproject.toml README.md ./
COPY src ./src

RUN pip install --upgrade pip

# Build condicional de dependências
RUN if [ "$INSTALL_VECTOR_DB" = "true" ]; then \
      pip wheel --no-cache-dir --wheel-dir /wheels .[vector-db]; \
    else \
      pip wheel --no-cache-dir --wheel-dir /wheels .; \
    fi

# -------------------------
# 🚀 STAGE 2 — RUNTIME
# -------------------------
FROM python:3.12-slim

WORKDIR /app

# 🔒 Variáveis padrão
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app/src \
    STORAGE=memory \
    APP_PROFILE=hybrid \
    WORKERS=2 \
    HOST=0.0.0.0 \
    PORT=8000

# Apenas runtime deps
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Instala dependências compiladas
COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir /wheels/*

# Copia apenas código necessário
COPY src ./src
COPY pyproject.toml .
COPY README.md .

# Cria usuário
RUN useradd -m appuser

# Criar e dar permissão
RUN mkdir -p /app/data /app/logs && chown -R appuser:appuser /app

# Troca usuário
USER appuser

# Porta
EXPOSE 8000

# Healthcheck robusto
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Start app (configurável por ENV)
CMD ["sh", "-c", "uvicorn rpg_narrative_server.app:app --host ${HOST} --port ${PORT} --workers ${WORKERS}"]
