from asyncpg import Connection


class TokenRepository:
    def __init__(self):
        pass

    async def buscar_por_username(
        self,
        conn: Connection,
        username: str,
    ) -> dict | None:
        row = await conn.fetchrow(
            "SELECT id, nome, username, password, niveis_acesso_id "
            "FROM administradores WHERE LOWER(username) = LOWER($1)",
            username,
        )
        if row is None:
            return None
        return {
            "id": row["id"],
            "nome": row["nome"],
            "username": row["username"],
            "password": row["password"],
            "niveis_acesso_id": row["niveis_acesso_id"],
        }
