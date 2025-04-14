from pydantic import BaseModel, EmailStr
from datetime import date
from typing import Optional



class ContactBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    birthday: date
    additional_info: Optional[str] = None

class ContactCreate(ContactBase):
    pass

class ContactUpdate(ContactBase):
    pass

class ContactRead(ContactBase):
    id: int

    class Config:
        from_attributes = True





class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    is_verified: bool
    avatar: Optional[str]

    class Config:
        from_attributes = True


class TokenModel(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginModel(BaseModel):
    email: EmailStr
    password: str