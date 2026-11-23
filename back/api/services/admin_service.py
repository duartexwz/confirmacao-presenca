from http import HTTPStatus

from asyncpg import Connection
from fastapi import HTTPException

from api.repositories.admin_repository import AdminRepository
from api.schemas.admin_schemas import (
    AdminFilter,
    AdminResponseSchemas,
    AdminSchemas,
    AdminUpdateSchema,
)
from api.security import get_password_hash


class AdminService:
    def __init__(self):
        self.admin_repository = AdminRepository()

    async def cadastrar_admin(self, conn: Connection, admin: AdminSchemas, **kwargs) -> AdminResponseSchemas:
        existe_nome = await self.admin_repository.buscar_administrador_por_nome(conn, admin.nome)

        if existe_nome:
            raise HTTPException(
                detail="Já existe um administrador cadastrado com este nome.", status_code=HTTPStatus.CONFLICT
            )

        existe_username = await self.admin_repository.buscar_administradores_por_email(conn, admin.username)

        if existe_username:
            raise HTTPException(
                detail="Já existe um administrador cadastrado com este username.", status_code=HTTPStatus.CONFLICT
            )

        dados = admin.model_dump()
        dados["password"] = get_password_hash(dados.pop("password"))

        result = await self.admin_repository.inserir_administrador(conn, dados)
        if not result:
            raise HTTPException(detail="Erro ao cadastrar admin", status_code=HTTPStatus.INTERNAL_SERVER_ERROR)

        return AdminResponseSchemas(**result)

    async def listar_admin(
        self, conn: Connection, filter: AdminFilter | None = None, **kwargs
    ) -> dict:
        offset = filter.offset if filter else 0
        limit = filter.limit if filter else 10
        result = await self.admin_repository.listar_administradores(conn, offset, limit)
        return {"administradores": result}

    async def atualizar_admin(
        self, conn: Connection, admin_id: int, admin: AdminUpdateSchema, **kwargs
    ) -> AdminResponseSchemas:
        nome_existe = await self.admin_repository.buscar_administrador_por_nome(conn, admin.nome, excluir_id=admin_id)

        if nome_existe:
            raise HTTPException(detail="Já existe um administrador com este nome.", status_code=HTTPStatus.CONFLICT)

        if admin.username:
            email_existe = await self.admin_repository.buscar_administradores_por_email(
                conn, admin.username, excluir_id=admin_id
            )

            if email_existe:
                raise HTTPException(
                    detail="Já existe um administrador com este username.", status_code=HTTPStatus.CONFLICT
                )

        dados = admin.model_dump(exclude_unset=True)

        nova_senha = dados.pop("password", None)
        if nova_senha is not None:
            dados["password"] = get_password_hash(nova_senha)

        if not dados:
            raise HTTPException(detail="Nenhum campo para atualizar", status_code=HTTPStatus.BAD_REQUEST)

        resultado = await self.admin_repository.atualizar_administradores(conn, admin_id, dados)

        if resultado is None:
            raise HTTPException(
                detail="Erro ao atualizar",
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            )

        return AdminResponseSchemas(**resultado)

    async def deletar_admin(self, conn: Connection, admin_id: int, **kwargs) -> dict:
        admin_existe = await self.admin_repository.buscar_administradores_por_id(conn, admin_id)

        if not admin_existe:
            raise HTTPException(detail="Nenhum admin encontrado", status_code=HTTPStatus.NOT_FOUND)

        await self.admin_repository.deletar_administradores(conn, admin_id)

        return {"message": "Administrador removido com sucesso"}
