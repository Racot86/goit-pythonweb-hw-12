
from fastapi import Depends, HTTPException, status
from src.dependencies.auth import get_current_user
from src.database.models import RoleEnum
from src.services.cache import CachedUser

def admin_required(current_user: CachedUser = Depends(get_current_user)):
    if current_user.role != RoleEnum.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admins only"
        )
    return current_user

