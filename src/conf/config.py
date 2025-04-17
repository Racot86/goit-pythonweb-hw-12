from pathlib import Path
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent.parent  # .../goit-pythonweb-hw-12

class Settings(BaseSettings):
    DATABASE_URL: str

    # поля, необов’язкові для локальних міграцій
    MAIL_USERNAME: str | None = None
    MAIL_PASSWORD: str | None = None
    MAIL_FROM: str | None = None
    MAIL_PORT: int | None = None
    MAIL_SERVER: str | None = None
    MAIL_FROM_NAME: str | None = None
    MAIL_STARTTLS: bool | None = None
    MAIL_SSL_TLS: bool | None = None

    CLOUDINARY_NAME: str | None = None
    CLOUDINARY_API_KEY: str | None = None
    CLOUDINARY_API_SECRET: str | None = None

    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_USER_TTL: int = 900

    # ⬇︎  Вкладений Config!
    class Config:
        env_file = BASE_DIR / ".env"   # абсолютний шлях
        env_file_encoding = "utf-8"


settings = Settings()