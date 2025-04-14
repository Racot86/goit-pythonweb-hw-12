from fastapi import APIRouter, Depends, Request
from src.database.models import User
from src.schemas import UserResponse
from src.dependencies.auth import get_current_user
from src.utils.limiter import limiter  # імпортуємо готовий limiter

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me", response_model=UserResponse)
@limiter.limit("5/minute")
def read_current_user(request: Request, current_user: User = Depends(get_current_user)):
    return current_user