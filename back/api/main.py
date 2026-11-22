"""
Ponto de entrada da aplicação FastAPI — Confirmação de Presença API.

Responsável por:
    - Instanciar a aplicação FastAPI com metadados da documentação.
    - Configurar CORS para permitir requisições do frontend.
    - Gerenciar o ciclo de vida do pool de conexões com o banco de dados.
    - Criar a tabela de confirmações automaticamente ao iniciar.
    - Registrar os routers da API.

Para executar:
    uvicorn api.main:app --reload
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.database import create_db_pool
from api.repositories.confirmacao_repository import criar_tabela_confirmacoes
from api.routers import confirmacao_router
from api.settings import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gerencia o ciclo de vida da aplicação.

    No startup:
        - Cria o pool de conexões com o PostgreSQL.
        - Cria a tabela `confirmacoes` caso não exista.

    No shutdown:
        - Fecha todas as conexões do pool.
    """
    # ── Startup ──
    app.state.pool = await create_db_pool()

    async with app.state.pool.acquire() as conn:
        await criar_tabela_confirmacoes(conn)

    yield

    # ── Shutdown ──
    await app.state.pool.close()


app = FastAPI(
    title="Confirmação de Presença API",
    description=(
        "API para gerenciar confirmações de presença do "
        "Jantar de Noivado — Mayckon & Duda. "
        "Permite registrar, listar, buscar e remover confirmações."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# ── CORS ──
# Permite que o frontend React (Vite) se comunique com a API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ──
app.include_router(confirmacao_router.router)


@app.get(
    "/",
    tags=["Health"],
    summary="Health check",
    description="Verifica se a API está no ar.",
)
async def health_check() -> dict:
    """Retorna status de saúde da API."""
    return {"status": "ok", "message": "API de Confirmação de Presença está ativa!"}
