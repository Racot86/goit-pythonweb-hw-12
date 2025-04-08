from sqlalchemy.ext.asyncio import AsyncSession
from src.repository import contacts as repo
from src.schemas import ContactCreate, ContactUpdate

async def get_contacts(skip: int, limit: int, db: AsyncSession):
    return await repo.get_contacts(skip, limit, db)

async def get_contact(contact_id: int, db: AsyncSession):
    return await repo.get_contact(contact_id, db)

async def create_contact(contact: ContactCreate, db: AsyncSession):
    return await repo.create_contact(contact, db)

async def update_contact(contact_id: int, contact_data: ContactUpdate, db: AsyncSession):
    return await repo.update_contact(contact_id, contact_data, db)

async def delete_contact(contact_id: int, db: AsyncSession):
    return await repo.delete_contact(contact_id, db)

async def search_contacts(query: str, db: AsyncSession):
    return await repo.search_contacts(query, db)

async def upcoming_birthdays(db: AsyncSession):
    return await repo.upcoming_birthdays(db)