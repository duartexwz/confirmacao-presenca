import uuid

import pytest

from api.services.confirmacao_service import confirmacao_service


@pytest.mark.asyncio
async def test_confirmar_presenca_sucesso(fake_db, client):
    fake_db.queue_fetchrow(None)  # buscar por nome
    fake_db.queue_fetchrow({"id": "11111111-2222-3333-4444-555555555555", "nome": "João"})

    # via service
    from api.schemas.confirmacao_schemas import ConfirmacaoCreate

    result = await confirmacao_service.confirmar_presenca(fake_db, ConfirmacaoCreate(nome="João"))
    assert result.nome == "João"
    assert result.id == "11111111-2222-3333-4444-555555555555"


@pytest.mark.asyncio
async def test_confirmar_presenca_duplicado(fake_db):
    fake_db.queue_fetchrow({"id": "11111111-2222-3333-4444-555555555555", "nome": "João"})

    from fastapi import HTTPException

    from api.schemas.confirmacao_schemas import ConfirmacaoCreate

    with pytest.raises(HTTPException) as exc:
        await confirmacao_service.confirmar_presenca(fake_db, ConfirmacaoCreate(nome="João"))
    assert exc.value.status_code == 409


@pytest.mark.asyncio
async def test_listar_confirmados(fake_db):
    fake_db.queue_fetchval(2)
    fake_db.queue_fetch([{"id": "a", "nome": "Ana"}, {"id": "b", "nome": "Bruno"}])

    result = await confirmacao_service.listar_confirmados(fake_db, offset=0, limit=10)
    assert result.total == 2
    assert len(result.confirmados) == 2
    assert result.confirmados[0].nome == "Ana"


@pytest.mark.asyncio
async def test_buscar_confirmacao_nao_encontrada(fake_db):
    fake_db.queue_fetchrow(None)
    uid = str(uuid.uuid4())

    from fastapi import HTTPException

    with pytest.raises(HTTPException) as exc:
        await confirmacao_service.buscar_confirmacao(fake_db, uid)
    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_remover_confirmacao_sucesso(fake_db):
    fake_db.queue_execute("DELETE 1")

    result = await confirmacao_service.remover_confirmacao(fake_db, str(uuid.uuid4()))
    assert "sucesso" in result["detail"] or "removida" in result["detail"]


@pytest.mark.asyncio
async def test_remover_confirmacao_nao_encontrada(fake_db):
    fake_db.queue_execute("DELETE 0")

    from fastapi import HTTPException

    with pytest.raises(HTTPException) as exc:
        await confirmacao_service.remover_confirmacao(fake_db, str(uuid.uuid4()))
    assert exc.value.status_code == 404
