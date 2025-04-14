from sqlalchemy.ext.asyncio import AsyncSession
from src.repository import contacts as repo
from src.schemas import ContactCreate, ContactUpdate
from src.database.models import User

async def get_contacts(skip: int, limit: int, db: AsyncSession, user: User):
    return await repo.get_contacts(skip, limit, db, user)

async def get_contact(contact_id: int, db: AsyncSession, user: User):
    return await repo.get_contact(contact_id, db, user)

async def create_contact(contact: ContactCreate, db: AsyncSession, user: User):
    return await repo.create_contact(contact, db, user)

async def update_contact(contact_id: int, contact_data: ContactUpdate, db: AsyncSession, user: User):
    return await repo.update_contact(contact_id, contact_data, db, user)

async def delete_contact(contact_id: int, db: AsyncSession, user: User):
    return await repo.delete_contact(contact_id, db, user)

async def search_contacts(query: str, db: AsyncSession, user: User):
    return await repo.search_contacts(query, db, user)

async def upcoming_birthdays(db: AsyncSession, user: User):
    return await repo.upcoming_birthdays(db, user)