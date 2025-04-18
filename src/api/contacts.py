from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from src.schemas import ContactRead, ContactCreate, ContactUpdate, UserResponse
from src.services import contacts as service
from src.database.db import get_db
from src.dependencies.auth import get_current_user
from src.database.models import User

router = APIRouter()

@router.get("/", response_model=List[ContactRead])
async def list_contacts(
    skip: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
        Retrieve a paginated list of the current user's contacts.

        :param skip: Number of records to skip (pagination).
        :param limit: Maximum number of records to return.
        :param db: Async SQLAlchemy session.
        :param current_user: The authenticated user.
        :return: List of contacts.
        """
    return await service.get_contacts(skip=skip, limit=limit, db=db, user=current_user)


@router.get("/{contact_id}", response_model=ContactRead)
async def get_contact(
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
        Retrieve a specific contact by ID.

        :param contact_id: The ID of the contact to retrieve.
        :param db: Async SQLAlchemy session.
        :param current_user: The authenticated user.
        :return: Contact if found, otherwise 404 error.
        """
    contact = await service.get_contact(contact_id=contact_id, db=db, user=current_user)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact


@router.post("/", response_model=ContactRead, status_code=201)
async def create_contact(
    contact: ContactCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
        Create a new contact for the current user.

        :param contact: ContactCreate schema with new contact data.
        :param db: Async SQLAlchemy session.
        :param current_user: The authenticated user.
        :return: Created contact.
        """
    return await service.create_contact(contact=contact, db=db, user=current_user)


@router.put("/{contact_id}", response_model=ContactRead)
async def update_contact(
    contact_id: int,
    contact: ContactUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
        Update an existing contact's information.

        :param contact_id: ID of the contact to update.
        :param contact: Updated data in ContactUpdate schema.
        :param db: Async SQLAlchemy session.
        :param current_user: The authenticated user.
        :return: Updated contact if found, otherwise 404.
        """
    updated = await service.update_contact(contact_id=contact_id, contact_data=contact, db=db, user=current_user)
    if not updated:
        raise HTTPException(status_code=404, detail="Contact not found")
    return updated


@router.delete("/{contact_id}", response_model=ContactRead)
async def delete_contact(
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
        Delete a contact by ID.

        :param contact_id: ID of the contact to delete.
        :param db: Async SQLAlchemy session.
        :param current_user: The authenticated user.
        :return: Deleted contact if found, otherwise 404.
        """
    deleted = await service.delete_contact(contact_id=contact_id, db=db, user=current_user)
    if not deleted:
        raise HTTPException(status_code=404, detail="Contact not found")
    return deleted


@router.get("/search/", response_model=List[ContactRead])
async def search_contacts(
    query: str = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
        Search for contacts by a given text query (name, email, etc.).

        :param query: Search string.
        :param db: Async SQLAlchemy session.
        :param current_user: The authenticated user.
        :return: List of matching contacts.
        """
    return await service.search_contacts(query=query, db=db, user=current_user)


@router.get("/birthdays/upcoming", response_model=List[ContactRead])
async def get_upcoming_birthdays(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    """
    Get contacts with upcoming birthdays within the next 7 days.

    :param db: Async SQLAlchemy session.
    :param current_user: The authenticated user.
    :return: List of contacts with upcoming birthdays.
    """
    return await service.upcoming_birthdays(db=db, user=current_user)


