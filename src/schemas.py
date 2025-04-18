from pydantic import BaseModel, EmailStr
from datetime import date
from typing import Optional

from enum import Enum

from uuid import UUID


class RoleEnum(str, Enum):
    """
        Enumeration of possible user roles.
        """
    user = "user"
    admin = "admin"


class ContactBase(BaseModel):
    """
        Base schema for a contact, used for shared attributes across create, update, and read models.
        """
    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    birthday: date
    additional_info: Optional[str] = None


class ContactCreate(ContactBase):
    """
        Schema for creating a new contact.
        Inherits all fields from ContactBase.
        """
    pass

class ContactUpdate(ContactBase):
    """
        Schema for updating an existing contact.
        Inherits all fields from ContactBase.
        """
    pass

class ContactRead(ContactBase):
    """
        Schema for reading a contact, includes the contact ID.
        """
    id: int

    class Config:
        from_attributes = True





class UserCreate(BaseModel):
    """
        Schema for user registration.
        """
    username: str
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """
        Schema for returning user data in responses.
        """
    id: int
    username: str
    email: EmailStr
    is_verified: bool
    avatar: Optional[str]
    role: RoleEnum

    class Config:
        from_attributes = True


class TokenModel(BaseModel):
    """
        Model representing a JWT access token response.
        """
    access_token: str
    token_type: str = "bearer"


class LoginModel(BaseModel):
    """
        Schema for user login.
        """
    email: EmailStr
    password: str

class PasswordResetRequest(BaseModel):
    """
        Schema for requesting a password reset by email.
        """
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    """
        Schema for confirming a password reset using a token and new password.
        """
    token: UUID
    new_password: str

class TokenRefreshRequest(BaseModel):
    """
    Request body model for refreshing access tokens.

    :field refresh_token: A valid refresh token issued during login.
    """
    refresh_token: str

class TokenResponse(BaseModel):
    """
    Response model for a new access token.

    :field access_token: The newly issued JWT access token.
    :field token_type: Type of the token (default: bearer).
    """
    access_token: str
    token_type: str = "bearer"