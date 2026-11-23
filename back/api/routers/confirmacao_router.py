"""
Rotas da API de confirmação de presença.

Define os endpoints REST para registrar, listar, buscar e remover
confirmações de presença dos convidados.

Endpoints:
    POST   /api/v1/confirmacoes       → Confirmar presença de um convidado.
    GET    /api/v1/confirmacoes       → Listar confirmações (paginado).
    GET    /api/v1/confirmacoes/{id}  → Buscar confirmação por UUID.
    DELETE /api/v1/confirmacoes/{id}  → Remover confirmação por UUID.
"""

from asyncpg import Connection
from fastapi import APIRouter, Depends, Query, status

from api.database import get_db
from api.schemas.confirmacao_schemas import (
    ConfirmacaoCreate,
    ConfirmacaoListResponse,
    ConfirmacaoResponse,
)
from api.services.confirmacao_service import confirmacao_service

router = APIRouter(
    prefix="/api/v1/confirmacoes",
    tags=["Confirmações de Presença"],
)


@router.post(
    "",
    response_model=ConfirmacaoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Confirmar presença",
    description="Registra a confirmação de presença de um convidado. Retorna erro 409 se o nome já estiver confirmado.",
)
async def confirmar_presenca(
    dados: ConfirmacaoCreate,
    conn: Connection = Depends(get_db),
) -> ConfirmacaoResponse:
    """
    Registra uma nova confirmação de presença.

    Args:
        dados: Corpo da requisição com o nome do convidado.
        conn: Conexão com o banco (injetada automaticamente).

    Returns:
        ConfirmacaoResponse: Dados da confirmação criada.
    """
    return await confirmacao_service.confirmar_presenca(conn, dados)


@router.get(
    "",
    response_model=ConfirmacaoListResponse,
    summary="Listar confirmações",
    description="Retorna a lista paginada de convidados que confirmaram presença.",
)
async def listar_confirmacoes(
    offset: int = Query(default=0, ge=0, description="Registros a pular."),
    limit: int = Query(default=10, ge=1, le=100, description="Registros por página."),
    conn: Connection = Depends(get_db),
) -> ConfirmacaoListResponse:
    """
    Lista todas as confirmações de presença com paginação.

    Args:
        offset: Número de registros a pular.
        limit: Número máximo de registros a retornar.
        conn: Conexão com o banco (injetada automaticamente).

    Returns:
        ConfirmacaoListResponse: Total e lista de confirmados.
    """
    return await confirmacao_service.listar_confirmados(conn, offset, limit)


@router.get(
    "/{confirmacao_id}",
    response_model=ConfirmacaoResponse,
    summary="Buscar confirmação",
    description="Retorna os dados de uma confirmação específica pelo UUID.",
)
async def buscar_confirmacao(
    confirmacao_id: str,
    conn: Connection = Depends(get_db),
) -> ConfirmacaoResponse:
    """
    Busca uma confirmação de presença pelo UUID.

    Args:
        confirmacao_id: UUID da confirmação.
        conn: Conexão com o banco (injetada automaticamente).

    Returns:
        ConfirmacaoResponse: Dados da confirmação encontrada.
    """
    return await confirmacao_service.buscar_confirmacao(conn, confirmacao_id)


@router.delete(
    "/{confirmacao_id}",
    status_code=status.HTTP_200_OK,
    summary="Remover confirmação",
    description="Remove uma confirmação de presença pelo UUID.",
)
async def remover_confirmacao(
    confirmacao_id: str,
    conn: Connection = Depends(get_db),
) -> dict:
    """
    Remove uma confirmação de presença existente.

    Args:
        confirmacao_id: UUID da confirmação a ser removida.
        conn: Conexão com o banco (injetada automaticamente).

    Returns:
        dict: Mensagem de confirmação de remoção.
    """
    return await confirmacao_service.remover_confirmacao(conn, confirmacao_id)
