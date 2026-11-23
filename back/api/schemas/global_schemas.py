from pydantic import BaseModel


class UsuarioLogado(BaseModel):
    id: int
    nome: str
    username: str
    niveis_acesso_id: int | None = None
