import redis.asyncio as redis
from pydantic import BaseModel
from src.conf.config import settings

redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=int(settings.REDIS_PORT),
    decode_responses=True,          # always str ↔︎ str → safer JSON
)

USER_TTL = int(settings.REDIS_USER_TTL or 900)


class CachedUser(BaseModel):        # what we actually store
    id: int
    username: str
    email: str
    is_verified: bool
    avatar: str | None = None

    @classmethod
    async def get(cls, email: str):
        raw = await redis_client.get(f"user:{email}")
        return cls.model_validate_json(raw) if raw else None

    async def save(self):
        await redis_client.setex(
            f"user:{self.email}",
            USER_TTL,
            self.model_dump_json(),
        )

    @staticmethod
    async def invalidate(email: str):
        await redis_client.delete(f"user:{email}")