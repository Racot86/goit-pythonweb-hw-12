import asyncio
from datetime import date, timedelta

import pytest
from fastapi import Depends
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool
from sqlalchemy import select


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


import src.database.db as db_mod
from src.database.db import get_db

db_mod.engine = engine
setattr(db_mod, 'AsyncSessionLocal', TestingSessionLocal)

from main import app
from src.database.models import Base, User
from src.services.auth import get_password_hash


TEST_USER = {
    "username": "johndoe",
    "email": "john@example.com",
    "password": "secret",
}

@pytest.fixture(scope="module", autouse=True)
def init_db():
    """Initialize the database and create a test user."""
    async def _init():

        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)

        async with TestingSessionLocal() as session:
            hashed = get_password_hash(TEST_USER["password"])
            user = User(
                username=TEST_USER["username"],
                email=TEST_USER["email"],
                password=hashed,
                is_verified=True,
            )
            session.add(user)
            await session.commit()
    asyncio.run(_init())

@pytest.fixture(scope="module")
def client():
    """Override app dependencies and yield a TestClient."""

    async def override_get_db():
        async with TestingSessionLocal() as session:
            yield session


    async def override_current_user(db=Depends(get_db)):
        result = await db.execute(select(User).filter_by(username=TEST_USER["username"]))
        return result.scalar_one()

    app.dependency_overrides[get_db] = override_get_db
    from src.dependencies.auth import get_current_user
    app.dependency_overrides[get_current_user] = override_current_user

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


def test_create_and_list(client):
    """Test creating contacts and listing them."""
    today = date.today()
    upcoming = (today + timedelta(days=3)).isoformat()
    beyond = (today + timedelta(days=20)).isoformat()


    first = {
        "first_name": "Alice",
        "last_name": "Smith",
        "email": "alice@example.com",
        "phone": "+123",
        "birthday": upcoming,
    }
    second = {
        "first_name": "Bob",
        "last_name": "Brown",
        "email": "bob@example.com",
        "phone": "+456",
        "birthday": beyond,
    }

    res1 = client.post("/contacts/", json=first)
    assert res1.status_code == 201
    id1 = res1.json()["id"]

    res2 = client.post("/contacts/", json=second)
    assert res2.status_code == 201
    id2 = res2.json()["id"]


    all_resp = client.get("/contacts/")
    assert all_resp.status_code == 200
    data = all_resp.json()
    ids = {c["id"] for c in data}
    assert id1 in ids and id2 in ids


def test_get_update_delete(client):
    """Test retrieving, updating, and deleting a contact."""

    get_resp = client.get(f"/contacts/1")
    assert get_resp.status_code == 200
    original = get_resp.json()


    update_payload = {**original, "first_name": "AliceX"}
    upd_resp = client.put("/contacts/1", json=update_payload)
    assert upd_resp.status_code == 200
    assert upd_resp.json()["first_name"] == "AliceX"


    del_resp = client.delete("/contacts/2")
    assert del_resp.status_code in (200, 204)

    assert client.get("/contacts/2").status_code == 404


def test_search_and_birthdays(client):
    """Test search and upcoming birthdays endpoints."""

    search = client.get("/contacts/search/", params={"query": "AliceX"})
    assert search.status_code == 200
    assert all("AliceX" in c["first_name"] for c in search.json())


    birth_resp = client.get("/contacts/birthdays/upcoming")
    assert birth_resp.status_code == 200
    results = birth_resp.json()
    assert all(
        date.fromisoformat(c["birthday"]) <= date.today() + timedelta(days=7)
        for c in results
    )
