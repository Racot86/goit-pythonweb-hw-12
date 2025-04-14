from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import declarative_base

from sqlalchemy import Boolean
from sqlalchemy.orm import relationship


Base = declarative_base()

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

    contacts = relationship("Contact", back_populates="owner")