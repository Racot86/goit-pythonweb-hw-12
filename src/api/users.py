from fastapi import Request
from src.database.models import User
from src.schemas import UserResponse
from src.dependencies.auth import get_current_user
from src.utils.limiter import limiter

from fastapi import UploadFile, File, Depends, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.db import get_db
from src.services.cloudinary_service import upload_avatar

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me", response_model=UserResponse)
@limiter.limit("5/minute")
def read_current_user(request: Request, current_user: User = Depends(get_current_user)):
    return current_user

@router.post("/avatar", response_model=UserResponse)
async def upload_user_avatar(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    avatar_url = await upload_avatar(file)
    current_user.avatar = avatar_url
    db.add(current_user)
    await db.commit()
    await db.refresh(current_user)
    return current_user