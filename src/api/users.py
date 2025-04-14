# src/api/users.py
from fastapi import APIRouter, Depends
from src.database.models import User
from src.schemas import UserResponse
from src.dependencies.auth import get_current_user

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me", response_model=UserResponse)
def read_current_user(current_user: User = Depends(get_current_user)):
    return current_user