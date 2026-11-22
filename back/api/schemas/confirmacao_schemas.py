"""
Schemas Pydantic para validação e serialização dos dados de confirmação de presença.

Schemas disponíveis:
    - ConfirmacaoCreate: Dados de entrada para criar uma confirmação (nome do convidado).
    - ConfirmacaoResponse: Dados de resposta de uma confirmação individual.
    - ConfirmacaoListResponse: Lista paginada de confirmações.
    - PaginacaoParams: Parâmetros de paginação (offset e limit).
"""

from pydantic import BaseModel, Field


class ConfirmacaoCreate(BaseModel):
    """
    Schema de entrada para registrar uma nova confirmação de presença.

    Attributes:
        nome: Nome completo do convidado. Deve ter entre 2 e 150 caracteres.
    """

    nome: str = Field(
        ...,
        min_length=2,
        max_length=150,
        examples=["José dos Campos Ribeiro"],
        description="Nome completo do convidado.",
    )


class ConfirmacaoResponse(BaseModel):
    """
    Schema de resposta para uma confirmação de presença individual.

    Attributes:
        id: Identificador único da confirmação (UUID).
        nome: Nome completo do convidado confirmado.
    """

    id: str
    nome: str


class ConfirmacaoListResponse(BaseModel):
    """
    Schema de resposta para listagem paginada de confirmações.

    Attributes:
        total: Número total de confirmações registradas.
        confirmados: Lista de convidados confirmados na página atual.
    """

    total: int
    confirmados: list[ConfirmacaoResponse]


class PaginacaoParams(BaseModel):
    """
    Parâmetros de paginação para consultas.

    Attributes:
        offset: Número de registros a pular (padrão: 0).
        limit: Número máximo de registros a retornar (padrão: 10, máximo: 100).
    """

    offset: int = Field(default=0, ge=0, description="Número de registros a pular.")
    limit: int = Field(
        default=10, ge=1, le=100, description="Quantidade de registros por página."
    )