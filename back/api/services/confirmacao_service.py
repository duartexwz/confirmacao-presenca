"""
Camada de serviço para confirmações de presença.

Contém a lógica de negócio que orquestra chamadas ao repositório,
valida regras e formata respostas. Os routers chamam este módulo
em vez de acessar o repositório diretamente.
"""

from asyncpg import Connection
from fastapi import HTTPException, status

from api.repositories.confirmacao_repository import ConfirmacoesRepository
from api.schemas.confirmacao_schemas import (
    ConfirmacaoCreate,
    ConfirmacaoListResponse,
    ConfirmacaoResponse,
)


class ConfirmacaoServices:
    def __init__(self):
        self.repo = ConfirmacoesRepository()

    async def confirmar_presenca(self, conn: Connection, dados: ConfirmacaoCreate) -> ConfirmacaoResponse:
        """
        Registra a confirmação de presença de um convidado.

        Verifica se o nome já foi confirmado anteriormente para evitar duplicatas.

        Args:
            conn: Conexão ativa com o banco de dados.
            dados: Schema de entrada contendo o nome do convidado.

        Returns:
            ConfirmacaoResponse: Dados da confirmação criada.

        Raises:
            HTTPException 409: Se o convidado já confirmou presença.
        """
        nome_formatado = dados.nome.strip()

        existente = await self.repo.buscar_confirmacao_por_nome(conn, nome_formatado)
        if existente:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"O convidado '{nome_formatado}' já confirmou presença.",
            )

        registro = await self.repo.inserir_confirmacao(conn, nome_formatado)
        return ConfirmacaoResponse(**registro)

    async def listar_confirmados(self, conn: Connection, offset: int = 0, limit: int = 10) -> ConfirmacaoListResponse:
        """
        Retorna a lista paginada de convidados confirmados.

        Args:
            conn: Conexão ativa com o banco de dados.
            offset: Número de registros a pular.
            limit: Quantidade de registros por página.

        Returns:
            ConfirmacaoListResponse: Objeto com total e lista de confirmados.
        """
        total = await self.repo.contar_confirmacoes(conn)
        confirmados = await self.repo.listar_confirmacoes(conn, offset, limit)

        return ConfirmacaoListResponse(
            total=total,
            confirmados=[ConfirmacaoResponse(**c) for c in confirmados],
        )

    async def buscar_confirmacao(self, conn: Connection, confirmacao_id: str) -> ConfirmacaoResponse:
        """
        Busca uma confirmação específica pelo seu UUID.

        Args:
            conn: Conexão ativa com o banco de dados.
            confirmacao_id: UUID da confirmação.

        Returns:
            ConfirmacaoResponse: Dados da confirmação encontrada.

        Raises:
            HTTPException 404: Se a confirmação não for encontrada.
        """
        registro = await self.repo.buscar_confirmacao_por_id(conn, confirmacao_id)
        if registro is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Confirmação não encontrada.",
            )
        return ConfirmacaoResponse(**registro)

    async def remover_confirmacao(self, conn: Connection, confirmacao_id: str) -> dict:
        """
        Remove uma confirmação de presença.

        Args:
            conn: Conexão ativa com o banco de dados.
            confirmacao_id: UUID da confirmação a ser removida.

        Returns:
            dict: Mensagem de sucesso.

        Raises:
            HTTPException 404: Se a confirmação não for encontrada.
        """
        deletado = await self.repo.deletar_confirmacao(conn, confirmacao_id)
        if not deletado:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Confirmação não encontrada.",
            )
        return {"detail": "Confirmação removida com sucesso."}


# ── Instância singleton usada pelos routers ──
confirmacao_service = ConfirmacaoServices()
