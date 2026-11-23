"""
Ponto de entrada da aplicação FastAPI — Confirmação de Presença API.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from api.database import create_db_pool
from api.repositories.admin_repository import AdminRepository
from api.repositories.confirmacao_repository import criar_tabela_confirmacoes
from api.routers import admin_router, confirmacao_router, login_router
from api.security import get_password_hash
from api.settings import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.pool = await create_db_pool()

    async with app.state.pool.acquire() as conn:
        await criar_tabela_confirmacoes(conn)

        admin_repo = AdminRepository()
        await admin_repo.criar_tabela_admin(conn)

        # Garante a existência do administrador padrão.
        admin_email = "mayckonkennedy877@gmail.com"
        existente = await admin_repo.buscar_administradores_por_email(conn, admin_email)
        if not existente:
            await admin_repo.inserir_administrador(
                conn,
                {
                    "nome": "Mayckon Kennedy",
                    "username": admin_email,
                    "password": get_password_hash("Mk@220525"),
                    "niveis_acesso_id": 1,
                },
            )

    app.state.limiter = login_router.limiter
    yield

    await app.state.pool.close()


app = FastAPI(
    title="Confirmação de Presença API",
    description="API para gerenciar confirmações de presença do Jantar de Noivado — Mayckon & Duda.",
    version="1.0.0",
    lifespan=lifespan,
)

app.state.limiter = login_router.limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.CORS_ORIGINS.split(",") if o.strip()],
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1)(:\d+)?|https://[a-zA-Z0-9-]+\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

app.include_router(confirmacao_router.router)
app.include_router(admin_router.router)
app.include_router(login_router.router)


@app.get("/", tags=["Health"])
async def health_check() -> dict:
    return {"status": "ok", "message": "API de Confirmação de Presença está ativa!"}
