import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi import Request, HTTPException
from src.api import auth as auth_api
from src.database.models import User
from src.schemas import UserCreate
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
@patch("src.api.auth.create_access_token", return_value="fake-access-token")
@patch("src.api.auth.send_verification_email", new_callable=AsyncMock)
@patch("src.api.auth.create_email_token", return_value="fake-email-token")
async def test_signup_success(mock_create_token, mock_send_email, mock_create_access_token):
    mock_db = AsyncMock(spec=AsyncSession)
    new_user = UserCreate(username="testuser", email="test@example.com", password="strongpassword")


    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_result

    mock_db.commit = AsyncMock()
    mock_db.refresh = AsyncMock()

    request = MagicMock(spec=Request)

    result = await auth_api.signup(user=new_user, request=request, db=mock_db)

    assert result["access_token"] == "fake-access-token"
    assert result["token_type"] == "bearer"
    mock_send_email.assert_awaited_once()
    mock_db.commit.assert_awaited()
    mock_db.refresh.assert_awaited()


@pytest.mark.asyncio
async def test_signup_conflict():
    mock_db = AsyncMock()
    existing_user = User(id=1, username="taken", email="test@example.com")

    mock_scalar_result = AsyncMock()
    mock_scalar_result.scalar_one_or_none = AsyncMock(return_value=existing_user)
    mock_db.execute.return_value = mock_scalar_result

    new_user = UserCreate(username="new", email="test@example.com", password="123")

    with pytest.raises(HTTPException) as exc:
        await auth_api.signup(user=new_user, request=MagicMock(), db=mock_db)

    assert exc.value.status_code == 409
    assert "Email already registered" in str(exc.value.detail)


@pytest.mark.asyncio
@patch("src.services.cache.redis_client.delete", new_callable=AsyncMock)
@patch("src.api.auth.decode_email_token", return_value="test@example.com")
async def test_verify_email_success(mock_decode, mock_redis_delete):
    mock_user = User(email="test@example.com", is_verified=False)
    mock_db = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none = MagicMock(return_value=mock_user)
    mock_db.execute.return_value = mock_result

    result = await auth_api.verify_email(token="valid-token", db=mock_db)

    assert result == {"message": "Email verified successfully."}
    assert mock_user.is_verified is True
    mock_redis_delete.assert_awaited_once()


@pytest.mark.asyncio
@patch("src.api.auth.decode_email_token", side_effect=Exception("Invalid token"))
async def test_verify_email_invalid_token(mock_decode):
    mock_db = AsyncMock()

    with pytest.raises(HTTPException) as exc:
        await auth_api.verify_email(token="invalid-token", db=mock_db)

    assert exc.value.status_code == 400
    assert "Invalid or expired token" in str(exc.value.detail)