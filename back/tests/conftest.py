import os

os.environ.setdefault("DATABASE_URL", "postgresql://u:p@localhost:5432/db")
os.environ.setdefault("DB_USER", "u")
os.environ.setdefault("DB_PASSWORD", "p")
os.environ.setdefault("DB_HOST", "localhost")
os.environ.setdefault("DB_PORT", "5432")
os.environ.setdefault("DB_NAME", "db")
os.environ.setdefault("SECRET_KEY", "segredo-de-teste")
os.environ.setdefault("CLIENT_ID", "1")
os.environ.setdefault("ACCESS_TOKEN", "x")
os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
os.environ.setdefault("ALGORITHM", "HS256")
os.environ.setdefault("CORS_ORIGINS", "http://localhost:5173")
os.environ.setdefault("CLIENT_SECRET", "x")

from collections import deque

import httpx
import pytest
import pytest_asyncio

from api.database import get_db
from api.main import app
from api.schemas.global_schemas import UsuarioLogado
from api.security import get_current_user

ADMIN_EMAIL = "mayckonkennedy877@gmail.com"


class FakeConnection:
    def __init__(self):
        self.calls = []
        self.fetch_queue = deque()
        self.fetchrow_queue = deque()
        self.fetchval_queue = deque()
        self.fetch_default = []
        self.fetchrow_default = None
        self.fetchval_default = None
        self.execute_results = deque()

    def queue_fetch(self, *results):
        for result in results:
            self.fetch_queue.append(result)
        return self

    def queue_fetchrow(self, *results):
        for result in results:
            self.fetchrow_queue.append(result)
        return self

    def queue_fetchval(self, *results):
        for result in results:
            self.fetchval_queue.append(result)
        return self

    def queue_execute(self, *results):
        for result in results:
            self.execute_results.append(result)
        return self

    async def fetch(self, query, *args):
        self.calls.append(("fetch", query, args))
        if self.fetch_queue:
            return self.fetch_queue.popleft()
        return self.fetch_default

    async def fetchrow(self, query, *args):
        self.calls.append(("fetchrow", query, args))
        if self.fetchrow_queue:
            return self.fetchrow_queue.popleft()
        return self.fetchrow_default

    async def fetchval(self, query, *args):
        self.calls.append(("fetchval", query, args))
        if self.fetchval_queue:
            return self.fetchval_queue.popleft()
        return self.fetchval_default

    async def execute(self, query, *args):
        self.calls.append(("execute", query, args))
        if self.execute_results:
            return self.execute_results.popleft()
        return "OK"

    def queries(self, method="fetchrow"):
        return [call[1] for call in self.calls if call[0] == method]

    def args_of(self, index=0, method="fetchrow"):
        chamadas = [call for call in self.calls if call[0] == method]
        return chamadas[index][2]


@pytest.fixture
def fake_db():
    return FakeConnection()


@pytest.fixture(autouse=True)
def override_db(fake_db):
    app.dependency_overrides[get_db] = lambda: fake_db
    yield fake_db
    app.dependency_overrides.pop(get_db, None)
    app.dependency_overrides.pop(get_current_user, None)


def login_as(usuario):
    if usuario is None:
        app.dependency_overrides.pop(get_current_user, None)
    else:
        app.dependency_overrides[get_current_user] = lambda: usuario


@pytest.fixture
def admin_user():
    return UsuarioLogado(
        id=1,
        nome="Mayckon Kennedy",
        username=ADMIN_EMAIL,
        niveis_acesso_id=1,
    )


@pytest.fixture
def as_admin(admin_user):
    login_as(admin_user)
    return admin_user


@pytest.fixture
def as_anon():
    login_as(None)
    return None


@pytest_asyncio.fixture
async def client():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://teste") as ac:
        yield ac
