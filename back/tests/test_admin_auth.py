import pytest

from api.security import get_password_hash
from api.services.login_services import TokenServices


@pytest.mark.asyncio
async def test_login_sucesso(fake_db):
    hashed = get_password_hash("Mk@220525")
    fake_db.queue_fetchrow(
        {
            "id": 1,
            "nome": "Mayckon Kennedy",
            "username": "mayckonkennedy877@gmail.com",
            "password": hashed,
            "niveis_acesso_id": 1,
        }
    )

    service = TokenServices()
    from fastapi.security import OAuth2PasswordRequestForm

    form = OAuth2PasswordRequestForm(
        username="mayckonkennedy877@gmail.com",
        password="Mk@220525",
        scope="",
        client_id=None,
        client_secret=None,
    )
    session = await service.login_for_access_token(conn=fake_db, form_data=form)
    assert "access_token" in session
    assert session["user"].username == "mayckonkennedy877@gmail.com"


@pytest.mark.asyncio
async def test_login_falha(fake_db):
    fake_db.queue_fetchrow(None)

    service = TokenServices()
    from fastapi import HTTPException
    from fastapi.security import OAuth2PasswordRequestForm

    form = OAuth2PasswordRequestForm(
        username="x@y.com",
        password="wrong",
        scope="",
        client_id=None,
        client_secret=None,
    )
    with pytest.raises(HTTPException) as exc:
        await service.login_for_access_token(conn=fake_db, form_data=form)
    assert exc.value.status_code == 401


@pytest.mark.asyncio
async def test_cadastrar_admin(fake_db, as_admin):
    # buscar por nome -> None, buscar por email -> None, inserir -> row
    fake_db.queue_fetchrow(None)
    fake_db.queue_fetchrow(None)
    fake_db.queue_fetchrow(
        {"id": 2, "nome": "Novo", "username": "novo@test.com", "niveis_acesso_id": 1}
    )

    from api.schemas.admin_schemas import AdminSchemas
    from api.services.admin_service import AdminService

    service = AdminService()
    admin = AdminSchemas(nome="Novo", username="novo@test.com", password="senha1234", niveis_acesso_id=1)
    result = await service.cadastrar_admin(conn=fake_db, admin=admin, current_user=as_admin)
    assert result.username == "novo@test.com"


@pytest.mark.asyncio
async def test_listar_admin(fake_db, as_admin):
    fake_db.queue_fetch(
        [{"id": 1, "nome": "Mayckon", "username": "mayckonkennedy877@gmail.com", "niveis_acesso_id": 1}]
    )

    from api.services.admin_service import AdminService

    service = AdminService()
    result = await service.listar_admin(conn=fake_db, current_user=as_admin)
    assert len(result["administradores"]) == 1
