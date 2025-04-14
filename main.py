from fastapi import FastAPI
from contextlib import asynccontextmanager
import uvicorn

from src.api import contacts
from src.database.models import Base
from src.database.db import engine

from src.api import auth


@asynccontextmanager
async def lifespan_app(_: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield



app = FastAPI(title="Contacts API", lifespan=lifespan_app)


app.include_router(contacts.router, prefix="/contacts", tags=["Contacts"])
app.include_router(auth.router)

# ⬇️ Запуск напряму
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)