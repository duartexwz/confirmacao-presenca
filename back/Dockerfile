# ── Dockerfile do Backend (FastAPI + asyncpg) ──
# Imagem multi-stage para produção enxuta.

# ── Stage 1: Instalar dependências ──
FROM python:3.12-slim AS builder

WORKDIR /app

# Instala poetry para resolver dependências
RUN pip install --no-cache-dir poetry

# Copia arquivos de dependência primeiro (cache de camadas Docker)
COPY pyproject.toml poetry.lock ./

# Exporta dependências para requirements.txt (evita instalar poetry em produção)
RUN poetry export -f requirements.txt --without-hashes -o requirements.txt

# ── Stage 2: Imagem de produção ──
FROM python:3.12-slim

WORKDIR /app

# Instala apenas as dependências compiladas
COPY --from=builder /app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código da aplicação
COPY api/ ./api/

# Porta exposta pela API
EXPOSE 8000

# Comando de execução com uvicorn
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
