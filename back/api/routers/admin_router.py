from http import HTTPStatus
from typing import Annotated

from asyncpg import Connection
from fastapi import APIRouter, Depends, Request

from api.database import get_db
from api.schemas.admin_schemas import AdminFilter, AdminSchemas, AdminUpdateSchema
from api.schemas.global_schemas import UsuarioLogado
from api.security import get_current_user
from api.services.admin_service import AdminService

T_Session = Annotated[Connection, Depends(get_db)]
T_CurrentUser = Annotated[UsuarioLogado, Depends(get_current_user)]
T_AdminFilter = Annotated[AdminFilter, Depends()]

router = APIRouter(prefix="/api/v1/admin", tags=["Admin"])

admin_service = AdminService()


@router.post("/", status_code=HTTPStatus.CREATED, summary="Cadastrar Admin")
async def create_admin(request: Request, conn: T_Session, current_user: T_CurrentUser, admin: AdminSchemas):
    return await admin_service.cadastrar_admin(conn=conn, current_user=current_user, admin=admin, request=request)


@router.get("/", summary="Listar administradores", status_code=HTTPStatus.OK)
async def listar_administradores(conn: T_Session, current_user: T_CurrentUser, filter: T_AdminFilter):
    return await admin_service.listar_admin(conn=conn, current_user=current_user, filter=filter)


@router.put("/{admin_id}", summary="Atualizar Administradores", status_code=HTTPStatus.OK)
async def atualizar_administradores(
    admin_id: int, request: Request, conn: T_Session, current_user: T_CurrentUser, admin: AdminUpdateSchema
):
    return await admin_service.atualizar_admin(
        conn=conn, current_user=current_user, admin_id=admin_id, admin=admin, request=request
    )


@router.delete("/{admin_id}", summary="Deletar Admin", status_code=HTTPStatus.OK)
async def deletar_admin(admin_id: int, request: Request, conn: T_Session, current_user: T_CurrentUser):
    return await admin_service.deletar_admin(conn=conn, admin_id=admin_id, current_user=current_user, request=request)
