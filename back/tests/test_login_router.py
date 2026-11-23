import pytest

from api.security import get_password_hash


@pytest.mark.asyncio
async def test_login_endpoint(client, fake_db):
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
    response = await client.post(
        "/api/v1/login",
        data={"username": "mayckonkennedy877@gmail.com", "password": "Mk@220525"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["username"] == "mayckonkennedy877@gmail.com"
