from typing import Optional

from pydantic import BaseModel, Field


class AdminSchemas(BaseModel):
    nome: str
    username: str
    password: str
    niveis_acesso_id: int = 1


class AdminResponseSchemas(BaseModel):
    id: int
    nome: str
    username: str
    niveis_acesso_id: int


class ListAdminResponse(BaseModel):
    administradores: list[AdminResponseSchemas]


class AdminUpdateSchema(BaseModel):
    nome: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None


class AdminFilter(BaseModel):
    nome: Optional[str] = None
    username: Optional[str] = None
    offset: int = 0
    limit: int = 10


class FilterPage(BaseModel):
    offset: int = Field(default=0, ge=0, description="Número de registros a pular.")
    limit: int = Field(default=10, ge=1, le=100, description="Quantidade de registros por página.")
