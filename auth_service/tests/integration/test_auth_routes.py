import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.db.base import Base
from app.main import app
from app.api.deps import get_db

DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine_test = create_async_engine(DATABASE_URL, echo=False)
TestingSessionLocal = async_sessionmaker(
    bind=engine_test,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def override_get_db():
    async with TestingSessionLocal() as session:
        yield session


@pytest_asyncio.fixture(autouse=True)
async def prepare_database():
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def client():
    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac
    app.dependency_overrides.clear()


async def test_register_user(client: AsyncClient):
    response = await client.post(
        "/auth/register",
        json={"email": "test@example.com", "password": "password123"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["role"] == "user"
    assert "password_hash" not in data


async def test_login_user(client: AsyncClient):
    await client.post(
        "/auth/register",
        json={"email": "test@example.com", "password": "password123"},
    )
    response = await client.post(
        "/auth/login",
        data={"username": "test@example.com", "password": "password123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


async def test_get_me(client: AsyncClient):
    await client.post(
        "/auth/register",
        json={"email": "test@example.com", "password": "password123"},
    )
    login_response = await client.post(
        "/auth/login",
        data={"username": "test@example.com", "password": "password123"},
    )
    token = login_response.json()["access_token"]

    response = await client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"


async def test_register_duplicate_email(client: AsyncClient):
    await client.post(
        "/auth/register",
        json={"email": "test@example.com", "password": "password123"},
    )
    response = await client.post(
        "/auth/register",
        json={"email": "test@example.com", "password": "otherpassword"},
    )
    assert response.status_code == 409


async def test_login_wrong_password(client: AsyncClient):
    await client.post(
        "/auth/register",
        json={"email": "test@example.com", "password": "password123"},
    )
    response = await client.post(
        "/auth/login",
        data={"username": "test@example.com", "password": "wrongpassword"},
    )
    assert response.status_code == 401


async def test_me_without_token(client: AsyncClient):
    response = await client.get("/auth/me")
    assert response.status_code == 401


async def test_me_with_invalid_token(client: AsyncClient):
    response = await client.get(
        "/auth/me",
        headers={"Authorization": "Bearer invalid.token.here"},
    )
    assert response.status_code == 401
