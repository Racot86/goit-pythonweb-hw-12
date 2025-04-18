from uuid import uuid4
from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, update
from fastapi import HTTPException, status

from src.database.models import User, PasswordResetToken
from src.services.mail import send_password_reset_email
from src.services.auth import get_password_hash

TOKEN_LIFETIME_MIN = 30


async def request_reset(email: str, db: AsyncSession) -> None:
    result = await db.execute(select(User).where(User.email == email))
    user: User | None = result.scalar_one_or_none()
    if not user:

        return

    token = uuid4()
    expires = datetime.utcnow() + timedelta(minutes=TOKEN_LIFETIME_MIN)

    await db.execute(
        insert(PasswordResetToken).values(
            user_id=user.id,
            token=token,
            expires_at=expires,
        )
    )
    await db.commit()

    await send_password_reset_email(user.email, user.username, str(token))


async def confirm_reset(token: str, new_password: str, db: AsyncSession) -> None:
    stmt = (
        select(PasswordResetToken)
        .where(PasswordResetToken.token == token)
        .where(PasswordResetToken.used.is_(False))
        .where(PasswordResetToken.expires_at > datetime.utcnow())
    )
    res = await db.execute(stmt)
    prt: PasswordResetToken | None = res.scalar_one_or_none()
    if not prt:
        raise HTTPException(status_code=400, detail="Invalid or expired token")


    await db.execute(
        update(User)
        .where(User.id == prt.user_id)
        .values(password=get_password_hash(new_password))
    )

    await db.execute(
        update(PasswordResetToken).where(
            PasswordResetToken.id == prt.id
        ).values(used=True)
    )
    await db.commit()