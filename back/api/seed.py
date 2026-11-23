"""Seed inicial: garante o administrador padrão."""

import asyncio
import os
import sys

import asyncpg

from api.repositories.admin_repository import AdminRepository
from api.security import get_password_hash
from api.settings import settings


async def main() -> int:
    admin_email = os.getenv("ADMIN_EMAIL", "mayckonkennedy877@gmail.com").strip()
    admin_password = os.getenv("ADMIN_PASSWORD", "Mk@220525")
    admin_nome = os.getenv("ADMIN_NOME", "Mayckon Kennedy").strip() or "Mayckon Kennedy"

    if not admin_email or not admin_password:
        print("Defina ADMIN_EMAIL e ADMIN_PASSWORD.")
        return 2

    pool = await asyncpg.create_pool(dsn=settings.DATABASE_URL)
    try:
        async with pool.acquire() as conn:
            repo = AdminRepository()
            await repo.criar_tabela_admin(conn)
            existente = await repo.buscar_administradores_por_email(conn, admin_email)
            if existente:
                print(f"Admin já existe (id={existente['id']}) — pulando.")
                return 0
            await repo.inserir_administrador(
                conn,
                {
                    "nome": admin_nome,
                    "username": admin_email,
                    "password": get_password_hash(admin_password),
                    "niveis_acesso_id": 1,
                },
            )
            print("Admin criado com sucesso.")
    finally:
        await pool.close()
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
