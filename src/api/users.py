from fastapi import Request
from src.database.models import User
from src.schemas import UserResponse
from src.dependencies.auth import get_current_user
from src.utils.limiter import limiter

from fastapi import UploadFile, File, Depends, APIRouter, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.db import get_db
from src.services.cloudinary_service import upload_avatar


from src.dependencies.roles import admin_required
from src.database.models import RoleEnum
from sqlalchemy import select

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession


from src.dependencies.auth import get_current_user
from src.services.cache import CachedUser
from src.database.models import User




from src.dependencies.roles import admin_required       # залишаємо
from src.database.models import RoleEnum
from sqlalchemy import select

# NEW helper: дістаємо ORM‑User на основі CachedUser
async def admin_user_required(
    cached_user: CachedUser = Depends(admin_required),
    db: AsyncSession = Depends(get_db),
) -> User:
    orm_user: User | None = await db.get(User, cached_user.id)
    if orm_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return orm_user



router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me", response_model=UserResponse)
@limiter.limit("5/minute")
def read_current_user(request: Request, current_user: User = Depends(get_current_user)):
    """
        Retrieve the current authenticated user's data.

        Rate-limited to 5 requests per minute.

        :param request: FastAPI Request object (used by limiter).
        :param current_user: User object from auth dependency.
        :return: Current user data.
        """
    return current_user

@router.post("/avatar", response_model=UserResponse)
async def upload_user_avatar(
    file: UploadFile = File(...),
    current_user: User = Depends(admin_user_required),
    db: AsyncSession = Depends(get_db)
):
    """
        Upload and set a new avatar image for the authenticated admin user.

        :param file: Uploaded avatar image file.
        :param current_user: Authenticated admin user (checked via admin_user_required).
        :param db: Async SQLAlchemy session.
        :return: Updated user with new avatar URL.
        """
    avatar_url = await upload_avatar(file)
    current_user.avatar = avatar_url
    db.add(current_user)
    await db.commit()
    await db.refresh(current_user)

    await CachedUser.invalidate(current_user.email)

    return current_user

@router.patch("/set-role/{user_id}")
async def set_user_role(
    user_id: int,
    role: RoleEnum,
    _: User = Depends(admin_required),
    db: AsyncSession = Depends(get_db)
):
    """
        Change the role of another user. Requires admin access.

        :param user_id: ID of the user whose role is to be changed.
        :param role: New role to assign (RoleEnum).
        :param _: Current admin user (dependency).
        :param db: Async SQLAlchemy session.
        :return: Success message with the updated role.
        """
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(404, "User not found")
    user.role = role
    await db.commit()
    await CachedUser.invalidate(user.email)
    return {"detail": f"Role set to {role.value}"}