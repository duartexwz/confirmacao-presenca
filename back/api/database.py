"""
Módulo de gerenciamento do pool de conexões com o banco de dados PostgreSQL.

Utiliza `asyncpg` para manter um pool de conexões assíncronas que é
compartilhado durante todo o ciclo de vida da aplicação FastAPI.

Funções:
    - create_db_pool: Cria e retorna o pool de conexões.
    - get_db: Dependency injection do FastAPI que fornece uma conexão
      a partir do pool para cada requisição.
"""

from typing import AsyncGenerator

import asyncpg
from asyncpg import Connection
from fastapi import Request

from api.settings import settings


async def create_db_pool() -> asyncpg.Pool:
    """
    Cria um pool de conexões assíncronas com o PostgreSQL.

    Returns:
        asyncpg.Pool: Pool de conexões pronto para uso.

    Raises:
        asyncpg.PostgresError: Se não for possível conectar ao banco.
    """
    return await asyncpg.create_pool(
        dsn=settings.DATABASE_URL,
        min_size=5,
        max_size=20,
    )


async def get_db(request: Request) -> AsyncGenerator[Connection, None]:
    """
    Fornece uma conexão do pool para a requisição atual (dependency injection).

    A conexão é automaticamente devolvida ao pool ao final da requisição.

    Args:
        request: Objeto Request do FastAPI que contém o estado da aplicação.

    Yields:
        asyncpg.Connection: Conexão ativa com o banco de dados.
    """
    async with request.app.state.pool.acquire() as connection:
        yield connection