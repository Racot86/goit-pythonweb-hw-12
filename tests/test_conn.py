import pytest
import sqlalchemy
from sqlalchemy.ext.asyncio import create_async_engine

# 🚀 in‑memory SQLite for tests
DBB_URL = "sqlite+aiosqlite:///:memory:"

@pytest.mark.asyncio
async def test_select_one():
    print("hello")
    engine = create_async_engine(
        DBB_URL,
        echo=True,
        future=True,
    )
    async with engine.connect() as conn:
        result = await conn.execute(sqlalchemy.text("SELECT 1"))
        assert result.scalar_one() == 1
    await engine.dispose()