from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from pydantic import EmailStr
from typing import Optional
from jose import jwt
from datetime import datetime, timedelta

from src.conf.config import settings

# Налаштування FastAPI-Mail
conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
    MAIL_STARTTLS=settings.MAIL_STARTTLS,
    MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
)

# Твій секрет і алгоритм
SECRET_KEY = "verysecret"
ALGORITHM = "HS256"


def create_email_token(email: str) -> str:
    """Генерує токен для підтвердження пошти"""
    to_encode = {"sub": email, "exp": datetime.utcnow() + timedelta(hours=1)}
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


async def send_verification_email(email: EmailStr, username: str, token: str):
    """Формує лист і надсилає посилання на підтвердження"""
    verify_link = f"http://localhost:8000/auth/verify?token={token}"

    message = MessageSchema(
        subject="Verify your email",
        recipients=[email],
        body=f"""
        <h3>Hi {username},</h3>
        <p>Please verify your email by clicking the link below:</p>
        <a href="{verify_link}">Verify Email</a>
        """,
        subtype="html"
    )



    fm = FastMail(conf)
    await fm.send_message(message)

def decode_email_token(token: str) -> Optional[str]:
    """Розкодовує токен і повертає email, якщо він валідний"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except jwt.ExpiredSignatureError:
        return None
    except jwt.JWTError:
        return None