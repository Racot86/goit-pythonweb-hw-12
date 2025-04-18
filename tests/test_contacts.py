import pytest
from unittest.mock import AsyncMock, MagicMock
from src.repository import contacts as repo
from src.schemas import ContactCreate, ContactUpdate
from src.database.models import Contact

@pytest.mark.asyncio
async def test_get_contacts():
    mock_db = AsyncMock()
    mock_user = MagicMock(id=1)
    mock_contact = Contact(
        id=1, first_name="John", last_name="Doe",
        email="john@example.com", phone="123", birthday="1990-01-01"
    )


    mock_scalars = MagicMock()
    mock_scalars.all.return_value = [mock_contact]

    mock_result = MagicMock()
    mock_result.scalars.return_value = mock_scalars

    mock_db.execute = AsyncMock(return_value=mock_result)

    result = await repo.get_contacts(skip=0, limit=10, db=mock_db, user=mock_user)
    assert result == [mock_contact]

@pytest.mark.asyncio
async def test_get_contact_found():
    mock_db = AsyncMock()
    mock_user = MagicMock(id=1)
    mock_contact = Contact(id=1, user_id=1)

    mock_result = AsyncMock()
    mock_result.scalar_one_or_none = AsyncMock(return_value=mock_contact)
    mock_db.execute = AsyncMock(return_value=mock_result)

    result = await repo.get_contact(1, mock_db, mock_user)
    assert await result == mock_contact

@pytest.mark.asyncio
async def test_get_contact_not_found():
    mock_db = AsyncMock()
    mock_user = MagicMock(id=1)

    mock_result = AsyncMock()
    mock_result.scalar_one_or_none = AsyncMock(return_value=None)
    mock_db.execute = AsyncMock(return_value=mock_result)

    result = await repo.get_contact(99, mock_db, mock_user)
    assert await result is None

@pytest.mark.asyncio
async def test_create_contact():
    mock_db = AsyncMock()
    mock_user = MagicMock(id=1)
    contact_data = ContactCreate(
        first_name="Alice", last_name="Smith", email="alice@example.com",
        phone="555-123", birthday="1992-03-04"
    )
    result = await repo.create_contact(contact_data, db=mock_db, user=mock_user)
    assert result.first_name == "Alice"
    assert mock_db.add.called
    assert mock_db.commit.called
    assert mock_db.refresh.called

@pytest.mark.asyncio
async def test_update_contact_found():
    mock_db = AsyncMock()
    mock_user = MagicMock(id=1)
    mock_contact = Contact(id=1, user_id=1)

    async def fake_get_contact(contact_id, db, user):
        return mock_contact

    repo.get_contact = fake_get_contact

    updated_data = ContactUpdate(
        first_name="Updated", last_name="Name", email="new@example.com",
        phone="111-222", birthday="1990-02-02"
    )

    result = await repo.update_contact(1, updated_data, mock_db, mock_user)
    assert result.first_name == "Updated"
    assert mock_db.commit.called
    assert mock_db.refresh.called

@pytest.mark.asyncio
async def test_update_contact_not_found():
    mock_db = AsyncMock()
    mock_user = MagicMock(id=1)

    async def fake_get_contact(contact_id, db, user):
        return None

    repo.get_contact = fake_get_contact

    updated_data = ContactUpdate(
        first_name="Fake", last_name="Test", email="test@example.com",
        phone="000-000", birthday="2000-01-01"
    )

    result = await repo.update_contact(999, updated_data, mock_db, mock_user)
    assert result is None

@pytest.mark.asyncio
async def test_delete_contact_found():
    mock_db = AsyncMock()
    mock_user = MagicMock(id=1)
    mock_contact = Contact(id=1, user_id=1)

    async def fake_get_contact(contact_id, db, user):
        return mock_contact

    repo.get_contact = fake_get_contact

    result = await repo.delete_contact(1, mock_db, mock_user)
    assert result == mock_contact
    assert mock_db.delete.called
    assert mock_db.commit.called

@pytest.mark.asyncio
async def test_delete_contact_not_found():
    mock_db = AsyncMock()
    mock_user = MagicMock(id=1)

    async def fake_get_contact(contact_id, db, user):
        return None

    repo.get_contact = fake_get_contact

    result = await repo.delete_contact(123, mock_db, mock_user)
    assert result is None
