import asyncio
from io import BytesIO
from datetime import date

import pytest
from fastapi import Depends
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool
from sqlalchemy import select
from unittest.mock import AsyncMock

# In-memory SQLite setup
SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
)

# 1) Monkey-patch production DB to use our in-memory engine/session
import src.database.db as db_mod
from src.database.db import get_db

db_mod.engine = engine
setattr(db_mod, 'AsyncSessionLocal', TestingSessionLocal)

# 2) Stub Cloudinary to avoid real uploads
import src.services.cloudinary_service as cloud_mod
async def fake_upload_avatar(file):
    return "http://test/avatar.png"
cloud_mod.upload_avatar = fake_upload_avatar

# 3) Stub Redis cache to avoid real Redis connections
import src.services.cache as cache_mod

class DummyRedisClient:
    def __init__(self):
        self.store = {}
    async def get(self, key):
        return self.store.get(key)
    async def setex(self, key, ttl, value):
        self.store[key] = value
    async def delete(self, key):
        self.store.pop(key, None)

cache_mod.redis_client = DummyRedisClient()

from main import app
from src.database.models import Base, User, RoleEnum
from src.services.auth import get_password_hash

# Test users
NORMAL_USER = {"username": "user1", "email": "user1@example.com", "password": "pass1"}
ADMIN_USER = {"username": "admin1", "email": "admin1@example.com", "password": "adminpass"}

@pytest.fixture(scope="module", autouse=True)
def init_db():
    """Create tables and two users: normal + admin."""
    async def runner():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
        async with TestingSessionLocal() as session:
            # Seed normal user
            h1 = get_password_hash(NORMAL_USER["password"])
            u1 = User(username=NORMAL_USER["username"], email=NORMAL_USER["email"], password=h1, is_verified=True)
            # Seed admin user
            h2 = get_password_hash(ADMIN_USER["password"])
            u2 = User(username=ADMIN_USER["username"], email=ADMIN_USER["email"], password=h2, is_verified=True, role=RoleEnum.admin)
            session.add_all([u1, u2])
            await session.commit()
    asyncio.run(runner())

@pytest.fixture(scope="module")
def client():
    """Override dependencies and yield TestClient."""

    async def override_get_db():
        async with TestingSessionLocal() as session:
            yield session

    async def override_current_user(db=Depends(get_db)):
        result = await db.execute(select(User).filter_by(username=NORMAL_USER["username"]))
        return result.scalar_one()

    # Apply overrides
    app.dependency_overrides[get_db] = override_get_db
    from src.dependencies.auth import get_current_user
    app.dependency_overrides[get_current_user] = override_current_user

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


def test_read_current_user(client):
    resp = client.get("/users/me")
    assert resp.status_code == 200
    data = resp.json()
    assert data["username"] == NORMAL_USER["username"]


def test_upload_avatar_as_admin(client):
    # Override to admin user
    async def admin_user(db=Depends(get_db)):
        result = await db.execute(select(User).filter_by(username=ADMIN_USER["username"]))
        return result.scalar_one()
    from src.dependencies.auth import get_current_user
    app.dependency_overrides[get_current_user] = admin_user

    files = {"file": ("avatar.png", BytesIO(b"imgdata"), "image/png")}
    resp = client.post("/users/avatar", files=files)
    assert resp.status_code == 200
    assert resp.json()["avatar"].startswith("http://test/avatar.png")


def test_set_user_role(client):
    # admin override still active
    resp = client.patch(f"/users/set-role/1?role=admin")
    assert resp.status_code == 200
    assert "Role set to admin" in resp.json()["detail"]
    # Confirm update in DB
    async def get_role():
        async with TestingSessionLocal() as session:
            user = await session.get(User, 1)
            return user.role
    assert asyncio.run(get_role()) == RoleEnum.admin
