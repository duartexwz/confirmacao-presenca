from datetime import datetime, timedelta
from http import HTTPStatus
from typing import Annotated
from zoneinfo import ZoneInfo

from asyncpg import Connection
from fastapi import Cookie, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jwt import DecodeError, ExpiredSignatureError, InvalidTokenError, decode, encode
from pwdlib import PasswordHash

from api.database import get_db
from api.schemas.enums import NiveisAcessoEnum
from api.schemas.global_schemas import UsuarioLogado
from api.settings import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/login/", auto_error=False)

Token = Annotated[str | None, Depends(oauth2_scheme)]
Database = Annotated[Connection, Depends(get_db)]

password_hash = PasswordHash.recommended()

ACCESS_LEVEL_ORDER = {NiveisAcessoEnum.ADMINISTRADOR.value: 1}


def _credentials_exception() -> HTTPException:
    return HTTPException(
        detail="Credenciais inválidas",
        status_code=HTTPStatus.FORBIDDEN,
        headers={"WWW-Authenticate": "Bearer"},
    )


async def create_access_token(data: dict) -> str:
    to_encode = data.copy()

    expire = datetime.now(tz=ZoneInfo("UTC")) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    to_encode.update({"exp": expire, "token_type": "access"})

    return encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


async def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()

    expire = datetime.now(tz=ZoneInfo("UTC")) + timedelta(
        days=settings.ACCESS_TOKEN_EXPIRE_DAYS
    )

    to_encode.update({"exp": expire, "token_type": "refresh"})

    return encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )


def decode_session_token(token: str) -> dict:
    return decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])


async def get_user_by_email(conn: Connection, username: str) -> UsuarioLogado:
    query_usuarios = """
        SELECT
            id,
            nome,
            username,
            niveis_acesso_id
        FROM administradores WHERE username = $1
    """

    user_record = await conn.fetchrow(query_usuarios, username)

    if not user_record:
        raise _credentials_exception()

    return UsuarioLogado(
        id=user_record["id"],
        nome=user_record["nome"],
        username=user_record["username"],
        niveis_acesso_id=user_record["niveis_acesso_id"],
    )


async def get_current_user(
    db: Database,
    token: Token = None,
    access_token: Annotated[str | None, Cookie(alias="access_token")] = None,
) -> UsuarioLogado:
    session_token = token or access_token

    if not session_token:
        raise _credentials_exception()

    try:
        payload = decode_session_token(session_token)
        token_type = payload.get("token_type")

        if token_type and token_type != "access":
            raise _credentials_exception()

        subject_email = payload.get("sub")
        if not subject_email:
            raise _credentials_exception()

    except (DecodeError, ExpiredSignatureError, InvalidTokenError):
        raise _credentials_exception()

    return await get_user_by_email(db, subject_email)


async def get_optional_current_user(
    db: Database,
    token: Token = None,
    access_token: Annotated[str | None, Cookie(alias="access_token")] = None,
) -> UsuarioLogado | None:

    if not (access_token or token):
        return None

    try:
        return await get_current_user(db, token, access_token)
    except HTTPException as exc:
        if exc.status_code in (HTTPStatus.UNAUTHORIZED, HTTPStatus.FORBIDDEN):
            return None
        raise


def verify_password(plain_password, hashed_password):
    return password_hash.verify(plain_password, hashed_password)


def get_password_hash(password) -> str:
    return password_hash.hash(password)


def requer_nivel_acesso(nivel_minimo: NiveisAcessoEnum):
    async def verificar(current_user: Annotated[UsuarioLogado, Depends(get_current_user)]):
        user_order = ACCESS_LEVEL_ORDER.get(current_user.niveis_acesso_id, 0)

        required_order = ACCESS_LEVEL_ORDER.get(nivel_minimo.value, 999)

        if user_order < required_order:
            raise HTTPException(detail="A ação requer elevação", status_code=HTTPStatus.FORBIDDEN)

        return current_user

    return verificar
