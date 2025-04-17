# scripts/create_admin.py
from src.database.db import AsyncSessionLocal, engine, Base
from src.database.models import User, RoleEnum
from src.services.auth import get_password_hash
import asyncio

async def main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        admin = User(
            username="admin",
            email="admin@example.com",
            password=get_password_hash("AdminPass123"),
            is_verified=True,
            role=RoleEnum.admin,
        )
        session.add(admin)
        await session.commit()

asyncio.run(main())