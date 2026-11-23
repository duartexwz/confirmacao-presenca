from http import HTTPStatus
from typing import Annotated

from asyncpg import Connection
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.security import OAuth2PasswordRequestForm
from slowapi import Limiter
from slowapi.util import get_remote_address

from api.database import get_db
from api.services.login_services import TokenServices
from api.settings import settings

T_Session = Annotated[Connection, Depends(get_db)]
T_FormData = Annotated[OAuth2PasswordRequestForm, Depends()]

router = APIRouter(prefix="/api/v1/login", tags=["Login"])

login_service = TokenServices()

limiter = Limiter(key_func=get_remote_address)


@router.post("", summary="Login", status_code=HTTPStatus.OK)
@limiter.limit("5/minute")
async def login(request: Request, response: Response, conn: T_Session, form_data: T_FormData):
    try:
        session = await login_service.login_for_access_token(conn=conn, form_data=form_data)

    except HTTPException:
        raise

    response.set_cookie(
        key="access_token",
        value=session["access_token"],
        httponly=True,
        samesite="lax",
        secure=False,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
    return session
