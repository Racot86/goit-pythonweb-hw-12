from sqlalchemy import Column, Integer, String, Date, ForeignKey, Enum, DateTime
from sqlalchemy.orm import declarative_base

from sqlalchemy import Boolean
from sqlalchemy.orm import relationship

from enum import Enum as PyEnum

from uuid import UUID
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

Base = declarative_base()

class RoleEnum(PyEnum):
    """
        Enumeration for user roles.
        """
    user = "user"
    admin = "admin"

class Contact(Base):

    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    phone = Column(String, nullable=False)
    birthday = Column(Date, nullable=False)
    additional_info = Column(String, nullable=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)


    owner = relationship("User", back_populates="contacts")

class User(Base):

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    is_verified = Column(Boolean, default=False)
    avatar = Column(String, nullable=True)

    role = Column(Enum(RoleEnum), default=RoleEnum.user, nullable=False)

    contacts = relationship("Contact", back_populates="owner")


class PasswordResetToken(Base):

    __tablename__ = "password_reset_tokens"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    token = Column(PG_UUID(as_uuid=True), unique=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    used = Column(Boolean, default=False, nullable=False)

    user = relationship("User")