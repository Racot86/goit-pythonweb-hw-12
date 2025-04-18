# 📇 Contacts REST API with FastAPI

A fully-featured **Contacts Management** REST API built with **FastAPI**, **SQLAlchemy (AsyncIO)**, **PostgreSQL**, and **Alembic**. This service provides JWT-based authentication, email verification, avatar uploads via Cloudinary, birthday filtering, rate limiting, and more.

---

## 📝 Table of Contents
1. [Tech Stack](#-tech-stack)
2. [Features](#-features)
3. [Getting Started](#-getting-started)
   - [Prerequisites](#prerequisites)
   - [Clone Repository](#clone-repository)
   - [Environment Variables](#environment-variables)
   - [Local Development](#local-development)
   - [Database Migrations](#database-migrations)
4. [Docker](#-docker)
5. [Running Tests](#running-tests)
6. [Code Structure](#code-structure)
7. [API Endpoints](#api-endpoints)
8. [Environment Variables](#environment-variables-1)
9. [Deployment](#deployment)
10. [Author](#author)
11. [License](#license)

---

## 🚀 Tech Stack
- **Language:** Python 3.12
- **Web Framework:** FastAPI
- **Database:** PostgreSQL
- **ORM:** SQLAlchemy (AsyncIO)
- **Migrations:** Alembic
- **Authentication:** JWT (PyJWT)
- **Email:** SMTP (e.g., SendGrid, Mailgun)
- **Storage:** Cloudinary for avatar uploads
- **Testing:** pytest, pytest-asyncio, pytest-cov
- **Containerization:** Docker, Docker Compose

---

## ✨ Features
- **User Authentication**: Signup, login, refresh tokens, password reset
- **Email Verification**: Send verification link on signup
- **Contacts CRUD**: Create, read, update, delete contacts
- **Birthday Filter**: List contacts with upcoming birthdays
- **Avatar Upload**: Store and serve user avatars via Cloudinary
- **Role-Based Access**: User and Admin roles
- **Rate Limiting**: Throttle requests to prevent abuse
- **CORS**: Configurable Cross-Origin Resource Sharing
- **Dockerized**: Easy local setup with Docker Compose

---

## 🏁 Getting Started

### Prerequisites
- [Python 3.12](https://www.python.org/downloads/)
- [Poetry](https://python-poetry.org/)
- [PostgreSQL](https://www.postgresql.org/) (or Docker)
- [Cloudinary account](https://cloudinary.com/) (for avatar storage)
- SMTP credentials for sending emails

### Clone Repository
```bash
git clone https://github.com/yourusername/contacts-fastapi.git
cd contacts-fastapi
```

### Environment Variables
Copy `.env.example` to `.env` and fill in the values:
```bash
cp .env.example .env
```

Required variables:
```
DATABASE_URL=postgresql+asyncpg://USER:PASSWORD@HOST:PORT/DB_NAME
JWT_SECRET_KEY=your_jwt_secret
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USER=...
SMTP_PASSWORD=...
CLOUDINARY_URL=cloudinary://API_KEY:API_SECRET@CLOUD_NAME
```

### Local Development
```bash
# Install dependencies
poetry install

# Run the server
uvicorn main:app --reload
```
Server will start at `http://127.0.0.1:8000`.

### Database Migrations
```bash
# Create migration
alembic revision --autogenerate -m "Add new table"

# Apply migrations
alembic upgrade head
```

---

## 🐳 Docker

A **Docker Compose** configuration is provided:
```yaml
version: '3.8'
services:
  db:
    image: postgres:15
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
      POSTGRES_DB: contactsdb
    ports:
      - '5432:5432'

  web:
    build: .
    command: uvicorn main:app --host 0.0.0.0 --port 8000
    volumes:
      - .:/app
    ports:
      - '8000:8000'
    depends_on:
      - db
```

```bash
# Build and start
docker-compose up --build
```
Visit `http://localhost:8000`.

---

## 🔍 Running Tests
```bash
# Run all tests with coverage
pytest --cov=src --cov-report=term-missing
```
Aim for **> 80%** coverage.

---

## 📂 Code Structure
```
├── alembic/                  # Alembic migrations
├── src/
│   ├── api/
│   │   ├── auth.py
│   │   ├── contacts.py
│   │   └── users.py
│   ├── database/
│   │   ├── db.py
│   │   └── models.py
│   ├── dependencies/
│   │   ├── auth.py
│   │   └── roles.py
│   ├── repository/
│   │   └── contacts.py
│   ├── schemas.py
│   ├── services/
│   │   ├── auth.py
│   │   ├── mail.py
│   │   ├── password_reset.py
│   │   └── cloudinary_service.py
│   ├── utils/
│   │   └── limiter.py
│   └── main.py                # FastAPI entrypoint
├── tests/                     # Unit & integration tests
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
└── alembic.ini
```

---

## 📦 API Endpoints
View the automatically generated docs:
- **Swagger UI**: `GET /docs`
- **ReDoc**: `GET /redoc`

Examples:
```bash
# Signup
curl -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"username":"user1","email":"user1@example.com","password":"secret"}'

# Login
curl -X POST http://localhost:8000/auth/login \
  -d "username=user1@example.com&password=secret"

# Create contact (authenticated)
curl -X POST http://localhost:8000/contacts \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"first_name":"John","last_name":"Doe","email":"john@example.com","birthday":"1990-01-01"}'
```

---

## 🌍 Deployment
The app can be deployed to platforms like **Render**, **Heroku**, **AWS ECS**, or **DigitalOcean App Platform**.

Ensure environment variables are set and the service binds to `$PORT` if required by the host.

---

## 🧑‍💻 Author
- **Dmytro Mayevsky** - [mayevskydv@gmail.com](mailto:mayevskydv@gmail.com)

---

## 📜 License
MIT License. See [LICENSE](LICENSE) for details.

