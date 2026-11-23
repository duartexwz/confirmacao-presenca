from http import HTTPStatus
from typing import Annotated

from asyncpg import Connection
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from api.repositories.token_repository import TokenRepository
from api.schemas.global_schemas import UsuarioLogado
from api.security import create_access_token, create_refresh_token, verify_password

oauth2_scheme = Annotated[OAuth2PasswordRequestForm, Depends()]


class TokenServices:
    def __init__(self):
        self.token_repository = TokenRepository()

    async def login_for_access_token(self, conn: Connection, form_data: oauth2_scheme):
        user_record = await self.token_repository.buscar_por_username(conn, form_data.username)

        if not user_record:
            raise HTTPException(detail="Usuário ou senha inválidos", status_code=HTTPStatus.UNAUTHORIZED)

        if not verify_password(form_data.password, user_record["password"]):
            raise HTTPException(detail="Usuário ou senha inválidos", status_code=HTTPStatus.UNAUTHORIZED)

        access_token = await create_access_token(
            data={"sub": user_record["username"], "niveis_acesso_id": user_record["niveis_acesso_id"]}
        )

        refresh_token = await create_refresh_token(
            data={"sub": user_record["username"], "niveis_acesso_id": user_record["niveis_acesso_id"]}
        )

        user = UsuarioLogado(
            id=user_record["id"],
            nome=user_record["nome"],
            username=user_record["username"],
            niveis_acesso_id=user_record["niveis_acesso_id"],
        )

        return {"access_token": access_token, "refresh_token": refresh_token, "user": user}
