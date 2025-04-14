from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.database.models import Contact, User
from src.schemas import ContactCreate, ContactUpdate
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from collections.abc import Sequence


async def get_contacts(skip: int, limit: int, db: AsyncSession, user: User) -> Sequence[Contact]:
    result = await db.execute(
        select(Contact).where(Contact.user_id == user.id).offset(skip).limit(limit)
    )
    return result.scalars().all()


async def get_contact(contact_id: int, db: AsyncSession, user: User) -> Optional[Contact]:
    result = await db.execute(
        select(Contact).where(Contact.id == contact_id, Contact.user_id == user.id)
    )
    return result.scalar_one_or_none()


async def create_contact(contact: ContactCreate, db: AsyncSession, user: User) -> Contact:
    new_contact = Contact(**contact.model_dump(), user_id=user.id)
    db.add(new_contact)
    try:
        await db.commit()
        await db.refresh(new_contact)
        return new_contact
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Contact with this email already exists"
        )


async def update_contact(contact_id: int, contact_data: ContactUpdate, db: AsyncSession, user: User) -> Optional[Contact]:
    contact = await get_contact(contact_id, db, user)
    if contact:
        for key, value in contact_data.model_dump().items():
            setattr(contact, key, value)
        await db.commit()
        await db.refresh(contact)
    return contact


async def delete_contact(contact_id: int, db: AsyncSession, user: User) -> Optional[Contact]:
    contact = await get_contact(contact_id, db, user)
    if contact:
        await db.delete(contact)
        await db.commit()
    return contact


async def search_contacts(query: str, db: AsyncSession, user: User) -> Sequence[Contact]:
    result = await db.execute(
        select(Contact).where(
            Contact.user_id == user.id,
            (Contact.first_name.ilike(f"%{query}%")) |
            (Contact.last_name.ilike(f"%{query}%")) |
            (Contact.email.ilike(f"%{query}%"))
        )
    )
    return result.scalars().all()


async def upcoming_birthdays(db: AsyncSession, user: User) -> Sequence[Contact]:
    today = datetime.today().date()
    upcoming = today + timedelta(days=7)
    result = await db.execute(
        select(Contact).where(
            Contact.user_id == user.id,
            Contact.birthday.between(today, upcoming)
        )
    )
    return result.scalars().all()