# 📇 Contacts API

An asynchronous REST API for managing contacts. Built with **FastAPI**, **PostgreSQL**, **SQLAlchemy (async)**, **Alembic**, and **Pydantic v2**, with Docker support.

---

## 🚀 Features

- Create new contacts
- Retrieve all contacts with pagination
- Search contacts by first name, last name, or email
- Retrieve a contact by ID
- Update or delete contacts
- Get contacts with upcoming birthdays in the next 7 days
- Email uniqueness check with proper error handling (`409 Conflict`)

---

## 🛠️ Tech Stack

- [FastAPI](https://fastapi.tiangolo.com/)
- [SQLAlchemy (async)](https://docs.sqlalchemy.org/en/20/)
- [Alembic](https://alembic.sqlalchemy.org/)
- [Pydantic v2](https://docs.pydantic.dev/)
- [PostgreSQL](https://www.postgresql.org/)
- [Docker](https://www.docker.com/)
- [Poetry](https://python-poetry.org/)

---

## 📦 Installation

### 1. Clone the repository

```bash
git clone https://github.com/your-username/goit-pythonweb-hw-08.git
cd goit-pythonweb-hw-08