from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.database.models import User
from src.database.db import get_db
from src.services.auth import SECRET_KEY, ALGORITHM

from src.services.cache import CachedUser
import json

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # 1️⃣ decode email from JWT
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str | None = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # 2️⃣ try Redis first
    cached = await CachedUser.get(email)
    if cached:
        return cached          # 🚀 zero DB hit

    # 3️⃣ fall back to DB & re‑cache
    stmt = select(User).where(User.email == email)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if user is None:
        raise credentials_exception

    await CachedUser(
        id=user.id,
        username=user.username,
        email=user.email,
        is_verified=user.is_verified,
        avatar=user.avatar,
    ).save()

    return user