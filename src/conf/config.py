from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str

    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_PORT: int
    MAIL_SERVER: str
    MAIL_FROM_NAME: str
    MAIL_STARTTLS: bool
    MAIL_SSL_TLS: bool

    CLOUDINARY_NAME: str
    CLOUDINARY_API_KEY: str
    CLOUDINARY_API_SECRET: str

    REDIS_HOST: str = "redis"  # sensible defaults
    REDIS_PORT: int = 6379
    REDIS_USER_TTL: int = 900

class Config:
        env_file = ".env"


settings = Settings()