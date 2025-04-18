from fastapi import APIRouter, Depends, HTTPException, status, Request

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi.security import OAuth2PasswordRequestForm

from src.schemas import UserCreate, TokenModel, TokenResponse, TokenRefreshRequest
from src.database.db import get_db
from src.database.models import User
from src.services.auth import get_password_hash, verify_password, create_access_token
from src.services.mail import create_email_token, send_verification_email, decode_email_token

from src.services.cache import CachedUser

from src.database.models import RoleEnum

from src.schemas import PasswordResetRequest, PasswordResetConfirm
from src.services.password_reset import request_reset, confirm_reset

from src.services import auth as auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=TokenModel)
async def signup(user: UserCreate, request: Request, db: AsyncSession = Depends(get_db)):
    stmt = select(User).where(User.email == user.email)
    result = await db.execute(stmt)
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )

    hashed_password = get_password_hash(user.password)
    new_user = User(
        username=user.username,
        email=user.email,
        password=hashed_password,
        is_verified=False,
        role = RoleEnum.user
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    # Send verification email
    email_token = create_email_token(new_user.email)
    await send_verification_email(new_user.email, new_user.username, email_token)

    token = create_access_token({"sub": new_user.email})
    return {"access_token": token, "token_type": "bearer"}


@router.get("/verify")
async def verify_email(token: str, db: AsyncSession = Depends(get_db)):
    try:
        email = decode_email_token(token)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    stmt = select(User).where(User.email == email)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_verified = True
    await db.commit()

    await CachedUser.invalidate(user.email)

    return {"message": "Email verified successfully."}


@router.post("/login", response_model=TokenModel)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    stmt = select(User).where(User.email == form_data.username)
    result = await db.execute(stmt)
    db_user = result.scalar_one_or_none()

    if not db_user or not verify_password(form_data.password, db_user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not db_user.is_verified:
        raise HTTPException(status_code=403, detail="Email is not verified")

    token = create_access_token({"sub": db_user.email})

    # 🔸 cache the safe subset
    await CachedUser(
        id=db_user.id,
        username=db_user.username,
        email=db_user.email,
        is_verified=db_user.is_verified,
        avatar=db_user.avatar,
        role=db_user.role,
    ).save()

    return {"access_token": token, "token_type": "bearer"}



@router.post("/password-reset-request", status_code=status.HTTP_202_ACCEPTED)
async def password_reset_request(body: PasswordResetRequest,
                                 db: AsyncSession = Depends(get_db)):
    await request_reset(body.email, db)
    return {"detail": "If the e‑mail exists, a reset link was sent"}

@router.post("/password-reset-confirm")
async def password_reset_confirm(body: PasswordResetConfirm,
                                 db: AsyncSession = Depends(get_db)):
    await confirm_reset(str(body.token), body.new_password, db)
    return {"detail": "Password reset successful"}

@router.post("/refresh", response_model=TokenResponse)
def refresh_token(payload: TokenRefreshRequest):
    data = auth_service.verify_refresh_token(payload.refresh_token)
    if data is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    access_token = auth_service.create_access_token({"sub": data.get("sub")})
    return TokenResponse(access_token=access_token)

