"""
Repositório de acesso ao banco de dados para confirmações de presença.

Contém todas as queries SQL executadas diretamente via asyncpg.
Cada função recebe uma conexão do pool e executa a operação correspondente.

Este módulo NÃO contém lógica de negócio — apenas acesso a dados.
"""

import uuid

from asyncpg import Connection


class ConfirmacoesRepository:
    def __init__(self):
        pass

    async def criar_tabela_confirmacoes(self, conn: Connection) -> None:
        """
        Cria a tabela `confirmacoes` no banco de dados caso ela não exista.

        A tabela armazena o id (UUID) e o nome de cada convidado confirmado,
        além da data/hora de criação do registro.

        Args:
            conn: Conexão ativa com o banco de dados.
        """
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS confirmacoes (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                nome VARCHAR(150) NOT NULL,
                criado_em TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
        """)
        await conn.execute("""
            ALTER TABLE confirmacoes
            ADD COLUMN IF NOT EXISTS criado_em TIMESTAMP WITH TIME ZONE DEFAULT NOW();
        """)

    async def inserir_confirmacao(self, conn: Connection, nome: str) -> dict:
        """
        Insere uma nova confirmação de presença no banco de dados.

        Args:
            conn: Conexão ativa com o banco de dados.
            nome: Nome completo do convidado.

        Returns:
            dict: Dicionário com `id` (str) e `nome` (str) do registro criado.
        """
        row = await conn.fetchrow(
            "INSERT INTO confirmacoes (nome) VALUES ($1) RETURNING id, nome",
            nome,
        )
        return {"id": str(row["id"]), "nome": row["nome"]}

    async def listar_confirmacoes(self, conn: Connection, offset: int = 0, limit: int = 10) -> list[dict]:
        """
        Retorna uma lista paginada de confirmações ordenadas por data de criação.

        Args:
            conn: Conexão ativa com o banco de dados.
            offset: Número de registros a pular.
            limit: Quantidade máxima de registros a retornar.

        Returns:
            list[dict]: Lista de dicionários com `id` e `nome` de cada confirmação.
        """
        rows = await conn.fetch(
            "SELECT id, nome FROM confirmacoes ORDER BY criado_em DESC OFFSET $1 LIMIT $2",
            offset,
            limit,
        )
        return [{"id": str(row["id"]), "nome": row["nome"]} for row in rows]

    async def contar_confirmacoes(self, conn: Connection) -> int:
        """
        Retorna o número total de confirmações registradas.

        Args:
            conn: Conexão ativa com o banco de dados.

        Returns:
            int: Total de registros na tabela `confirmacoes`.
        """
        return await conn.fetchval("SELECT COUNT(*) FROM confirmacoes")

    async def buscar_confirmacao_por_id(self, conn: Connection, confirmacao_id: str) -> dict | None:
        """
        Busca uma confirmação específica pelo seu UUID.

        Args:
            conn: Conexão ativa com o banco de dados.
            confirmacao_id: UUID da confirmação a ser buscada.

        Returns:
            dict | None: Dicionário com `id` e `nome` se encontrado, ou None.
        """
        try:
            uid = uuid.UUID(confirmacao_id)
        except ValueError:
            return None

        row = await conn.fetchrow(
            "SELECT id, nome FROM confirmacoes WHERE id = $1",
            uid,
        )
        if row is None:
            return None
        return {"id": str(row["id"]), "nome": row["nome"]}

    async def deletar_confirmacao(self, conn: Connection, confirmacao_id: str) -> bool:
        """
        Remove uma confirmação de presença pelo UUID.

        Args:
            conn: Conexão ativa com o banco de dados.
            confirmacao_id: UUID da confirmação a ser removida.

        Returns:
            bool: True se o registro foi deletado, False se não existia.
        """
        try:
            uid = uuid.UUID(confirmacao_id)
        except ValueError:
            return False

        result = await conn.execute(
            "DELETE FROM confirmacoes WHERE id = $1",
            uid,
        )
        # asyncpg retorna algo como "DELETE 1" ou "DELETE 0"
        return result == "DELETE 1"

    async def buscar_confirmacao_por_nome(self, conn: Connection, nome: str) -> dict | None:
        """
        Busca uma confirmação pelo nome exato do convidado (case-insensitive).

        Útil para verificar se um convidado já confirmou presença.

        Args:
            conn: Conexão ativa com o banco de dados.
            nome: Nome do convidado a ser buscado.

        Returns:
            dict | None: Dicionário com `id` e `nome` se encontrado, ou None.
        """
        row = await conn.fetchrow(
            "SELECT id, nome FROM confirmacoes WHERE LOWER(nome) = LOWER($1)",
            nome,
        )
        if row is None:
            return None
        return {"id": str(row["id"]), "nome": row["nome"]}


# ── Função de conveniência para o lifespan (retrocompatibilidade) ──
async def criar_tabela_confirmacoes(conn: Connection) -> None:
    """Wrapper para uso direto no lifespan da aplicação."""
    repo = ConfirmacoesRepository()
    await repo.criar_tabela_confirmacoes(conn)
