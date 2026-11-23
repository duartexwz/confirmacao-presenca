from asyncpg import Connection


class AdminRepository:
    def __init__(self):
        pass

    async def criar_tabela_admin(self, conn: Connection) -> None:
        await conn.execute(
            """
                CREATE TABLE IF NOT EXISTS administradores(
                    id SERIAL PRIMARY KEY,
                    nome VARCHAR(100) UNIQUE,
                    username VARCHAR(255) UNIQUE,
                    password VARCHAR(255),
                    niveis_acesso_id INTEGER DEFAULT 1
                );
            """
        )

    async def inserir_administrador(
        self, conn: Connection, dados: dict
    ) -> dict | None:
        row = await conn.fetchrow(
            """
            INSERT INTO administradores (nome, username, password, niveis_acesso_id)
            VALUES ($1, $2, $3, $4)
            RETURNING id, nome, username, niveis_acesso_id
            """,
            dados["nome"],
            dados["username"],
            dados["password"],
            dados.get("niveis_acesso_id", 1),
        )
        if row is None:
            return None
        return {
            "id": row["id"],
            "nome": row["nome"],
            "username": row["username"],
            "niveis_acesso_id": row["niveis_acesso_id"],
        }

    async def listar_administradores(
        self, conn: Connection, offset: int = 0, limit: int = 10
    ) -> list[dict]:
        rows = await conn.fetch(
            "SELECT id, nome, username, niveis_acesso_id FROM administradores ORDER BY id DESC OFFSET $1 LIMIT $2",
            offset,
            limit,
        )
        return [
            {
                "id": row["id"],
                "nome": row["nome"],
                "username": row["username"],
                "niveis_acesso_id": row["niveis_acesso_id"],
            }
            for row in rows
        ]

    async def buscar_administradores_por_id(
        self, conn: Connection, administrador_id: int
    ) -> dict | None:
        row = await conn.fetchrow(
            "SELECT id, nome, username, niveis_acesso_id FROM administradores WHERE id = $1",
            administrador_id,
        )
        if row is None:
            return None
        return {
            "id": row["id"],
            "nome": row["nome"],
            "username": row["username"],
            "niveis_acesso_id": row["niveis_acesso_id"],
        }

    async def deletar_administradores(
        self, conn: Connection, administrador_id: int
    ) -> bool:
        result = await conn.execute(
            "DELETE FROM administradores WHERE id = $1",
            administrador_id,
        )
        return result == "DELETE 1"

    async def atualizar_administradores(
        self, conn: Connection, administrador_id: int, dados: dict
    ) -> dict | None:
        # Monta SET dinâmico
        campos = list(dados.keys())
        valores = list(dados.values())

        if not campos:
            return None

        set_clause = ", ".join(
            f"{campo} = ${i + 1}" for i, campo in enumerate(campos)
        )
        valores.append(administrador_id)
        param_id = f"${len(valores)}"

        row = await conn.fetchrow(
            f"UPDATE administradores SET {set_clause} WHERE id = {param_id} "
            f"RETURNING id, nome, username, niveis_acesso_id",
            *valores,
        )
        if row is None:
            return None
        return {
            "id": row["id"],
            "nome": row["nome"],
            "username": row["username"],
            "niveis_acesso_id": row["niveis_acesso_id"],
        }

    async def buscar_administrador_por_nome(
        self, conn: Connection, nome: str, excluir_id: int | None = None
    ) -> dict | None:
        if excluir_id is not None:
            row = await conn.fetchrow(
                "SELECT id, nome, username FROM administradores WHERE LOWER(nome) = LOWER($1) AND id != $2",
                nome,
                excluir_id,
            )
        else:
            row = await conn.fetchrow(
                "SELECT id, nome, username FROM administradores WHERE LOWER(nome) = LOWER($1)",
                nome,
            )
        if row is None:
            return None
        return {"id": row["id"], "nome": row["nome"], "username": row["username"]}

    async def buscar_administradores_por_email(
        self, conn: Connection, username: str, excluir_id: int | None = None
    ) -> dict | None:
        if excluir_id is not None:
            row = await conn.fetchrow(
                "SELECT id, nome, username FROM administradores WHERE LOWER(username) = LOWER($1) AND id != $2",
                username,
                excluir_id,
            )
        else:
            row = await conn.fetchrow(
                "SELECT id, nome, username FROM administradores WHERE LOWER(username) = LOWER($1)",
                username,
            )
        if row is None:
            return None
        return {"id": row["id"], "nome": row["nome"], "username": row["username"]}
