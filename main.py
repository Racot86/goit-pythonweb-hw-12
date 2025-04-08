from fastapi import FastAPI
from contextlib import asynccontextmanager
import uvicorn

from src.api import contacts
from src.database.models import Base
from src.database.db import engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield  # тут FastAPI запускається

    # Shutdown (можна додати логіку тут)
    # print("Shutting down...")


app = FastAPI(title="Contacts API", lifespan=lifespan)


app.include_router(contacts.router, prefix="/contacts", tags=["Contacts"])

# ⬇️ Запуск напряму
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)