import pytest
from unittest.mock import AsyncMock, MagicMock
from src.api import users as users_api
from src.schemas import UserResponse
from src.database.models import User, RoleEnum
from starlette.requests import Request


@pytest.mark.asyncio
async def test_read_current_user():
    mock_user = MagicMock(spec=User)
    mock_user.id = 1
    mock_user.username = "testuser"
    mock_user.email = "test@example.com"
    mock_user.is_verified = True
    mock_user.avatar = "http://example.com/avatar.png"
    mock_user.role = RoleEnum.user

    request = Request(scope={"type": "http", "headers": [], "method": "GET", "path": "/users/me"})
    result = users_api.read_current_user(request=request, current_user=mock_user)
    assert result == mock_user


@pytest.mark.asyncio
async def test_upload_user_avatar(monkeypatch):
    mock_user = MagicMock(spec=User)
    mock_user.email = "test@example.com"
    mock_user.id = 1

    mock_db = AsyncMock()

    mock_file = AsyncMock()
    mock_file.filename = "avatar.png"
    mock_file.read.return_value = b"image data"

    monkeypatch.setattr("src.api.users.upload_avatar", AsyncMock(return_value="http://cloud.url/avatar.jpg"))
    monkeypatch.setattr("src.api.users.CachedUser.invalidate", AsyncMock())

    updated_user = await users_api.upload_user_avatar(file=mock_file, current_user=mock_user, db=mock_db)
    assert updated_user.avatar == "http://cloud.url/avatar.jpg"
    assert mock_db.commit.called
    assert mock_db.refresh.called


@pytest.mark.asyncio
async def test_set_user_role(monkeypatch):
    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlalchemy.engine import Result

    mock_user = MagicMock()
    mock_user.email = "test@example.com"

    mock_db = AsyncMock(spec=AsyncSession)

    mock_result = AsyncMock(spec=Result)
    target_user = MagicMock(spec=User)
    mock_result.scalar_one_or_none.return_value = target_user
    mock_db.execute.return_value = mock_result

    monkeypatch.setattr("src.api.users.CachedUser.invalidate", AsyncMock())

    response = await users_api.set_user_role(user_id=1, role=RoleEnum.admin, _=mock_user, db=mock_db)
    assert response == {"detail": "Role set to admin"}
    assert target_user.role == RoleEnum.admin
    assert mock_db.commit.called