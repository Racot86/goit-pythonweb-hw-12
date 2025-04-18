import pytest
import asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

from main import app
from src.database.models import Base, User
from src.database.models import PasswordResetToken
from src.database.db import get_db
from src.services.auth import get_password_hash


DATABASE_URL = "sqlite+aiosqlite:///:memory:"
engine = create_async_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = async_sessionmaker(
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
    bind=engine,
)

test_user = {
    "id": 1,
    "username": "testuser",
    "email": "user1@example.com",
    "password": "testpass",
}

@pytest.fixture(scope="module", autouse=True)
def init_db():
    """Create tables and seed a test user."""
    async def _init():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)

        async with TestingSessionLocal() as session:
            hashed = get_password_hash(test_user["password"])
            user = User(
                username=test_user["username"],
                email=test_user["email"],
                password=hashed,
            )

            user.is_verified = True
            session.add(user)
            await session.commit()
    asyncio.run(_init())

@pytest.fixture(scope="module")
def client():
    # Override the database dependency
    async def override_get_db():
        async with TestingSessionLocal() as session:
            yield session
    app.dependency_overrides[get_db] = override_get_db

    # Stub out Redis cache
    import src.services.cache as cache_mod
    class DummyRedisClient:
        async def setex(self, *args, **kwargs):
            pass
        async def delete(self, *args, **kwargs):
            pass
    cache_mod.redis_client = DummyRedisClient()


    import src.services.mail as mail_mod
    mail_mod.send_password_reset_email = lambda email, token: None

    yield TestClient(app)

# --- Integration Tests ---

def test_signup(client):
    resp = client.post(
        "/auth/signup",
        json={
            "username": "newuser",
            "email": "new@example.com",
            "password": "newpass",
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data


def test_login(client):
    resp = client.post(
        "/auth/login",
        data={
            "username": test_user["email"],
            "password": test_user["password"],
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data


def test_password_reset_request(client):
    resp = client.post(
        "/auth/password-reset-request",
        json={"email": test_user["email"]},
    )
    assert resp.status_code == 202
