from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from src.schemas import ContactRead, ContactCreate, ContactUpdate
from src.services import contacts as service
from src.database.db import get_db

router = APIRouter()

@router.get("/", response_model=List[ContactRead])
async def list_contacts(skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db)):
    return await service.get_contacts(skip, limit, db)


@router.get("/{contact_id}", response_model=ContactRead)
async def get_contact(contact_id: int, db: AsyncSession = Depends(get_db)):
    contact = await service.get_contact(contact_id, db)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact


@router.post("/", response_model=ContactRead, status_code=201)
async def create_contact(contact: ContactCreate, db: AsyncSession = Depends(get_db)):
    return await service.create_contact(contact, db)


@router.put("/{contact_id}", response_model=ContactRead)
async def update_contact(contact_id: int, contact: ContactUpdate, db: AsyncSession = Depends(get_db)):
    updated = await service.update_contact(contact_id, contact, db)
    if not updated:
        raise HTTPException(status_code=404, detail="Contact not found")
    return updated


@router.delete("/{contact_id}", response_model=ContactRead)
async def delete_contact(contact_id: int, db: AsyncSession = Depends(get_db)):
    deleted = await service.delete_contact(contact_id, db)
    if not deleted:
        raise HTTPException(status_code=404, detail="Contact not found")
    return deleted


@router.get("/search/", response_model=List[ContactRead])
async def search_contacts(query: str = Query(...), db: AsyncSession = Depends(get_db)):
    return await service.search_contacts(query, db)


@router.get("/birthdays/upcoming", response_model=List[ContactRead])
async def get_upcoming_birthdays(db: AsyncSession = Depends(get_db)):
    return await service.upcoming_birthdays(db)