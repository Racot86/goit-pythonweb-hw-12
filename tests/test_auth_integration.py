from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
import uuid, time

from src.database.db import get_db
from src.database.models import User, PasswordResetToken
from src.services.auth import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    create_email_token,
    decode_email_token,
)
from src.services.mail import send_verification_email, send_password_reset_email

router = APIRouter(prefix="/auth")


@router.post("/signup")
async def signup(data: dict, db=Depends(get_db)):
    # Create new user and send verification email
    new_user = User(
        username=data["username"],
        email=data["email"],
        hashed_password=get_password_hash(data["password"]),
        is_verified=False,
    )
    db.add(new_user)
    await db.commit()
    token = create_email_token(new_user.email)
    send_verification_email(new_user.email, token)
    access_token = create_access_token({"sub": new_user.email})
    return {"access_token": access_token}


@router.get("/verify")
async def verify_email(token: str, db=Depends(get_db)):
    email = decode_email_token(token)
    result = await db.execute(select(User).filter_by(email=email))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_verified = True
    await db.commit()
    return {"message": "Email verified"}


@router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db=Depends(get_db),
):
    result = await db.execute(select(User).filter_by(email=form_data.username))
    user = result.scalar_one_or_none()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token = create_access_token({"sub": user.email})
    refresh_token = create_refresh_token({"sub": user.email})
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.post("/refresh")
async def refresh_token_endpoint(body: dict, db=Depends(get_db)):
    try:
        payload = decode_refresh_token(body.get("refresh_token", ""))
        email = payload.get("sub")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    result = await db.execute(select(User).filter_by(email=email))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    new_access = create_access_token({"sub": email})
    return {"access_token": new_access}


@router.post("/password-reset-request", status_code=status.HTTP_202_ACCEPTED)
async def password_reset_request(body: dict, db=Depends(get_db)):
    result = await db.execute(select(User).filter_by(email=body.get("email", "")))
    user = result.scalar_one_or_none()
    if user:
        token = uuid.uuid4()
        expires = time.time() + 3600  # 1 hour from now
        prt = PasswordResetToken(user_id=user.id, token=token, expires_at=expires)
        db.add(prt)
        await db.commit()
        send_password_reset_email(user.email, str(token))
    return {}


@router.post("/password-reset-confirm")
async def password_reset_confirm(body: dict, db=Depends(get_db)):
    try:
        token_val = uuid.UUID(body.get("token", ""))
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid token format")
    result = await db.execute(select(PasswordResetToken).filter_by(token=token_val))
    prt = result.scalar_one_or_none()
    if not prt or prt.used or prt.expires_at < time.time():
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    # Update user password
    result = await db.execute(select(User).filter_by(id=prt.user_id))
    user = result.scalar_one()
    user.hashed_password = get_password_hash(body.get("new_password", ""))
    prt.used = True
    await db.commit()
    return {}
