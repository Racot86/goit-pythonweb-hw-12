# 📇 Contacts REST API with FastAPI

This project is a backend REST API for managing contacts. Built with **FastAPI**, **PostgreSQL**, and **Docker**, it includes features like user authentication, email verification, avatar upload via **Cloudinary**, and more.

---

## 🚀 Features

- 🧾 CRUD for contacts (name, email, birthday, etc.)
- 🔐 JWT-based authentication
- 📧 Email verification with SMTP
- ☁️ Avatar upload to Cloudinary
- 📅 Birthday filter (next 7 days)
- 🐳 Docker support (App + PostgreSQL)
- 🌍 CORS & Rate limiting
- 🔄 Alembic migrations

---

## 🛠 Technologies

- Python 3.12
- FastAPI
- SQLAlchemy + Alembic
- PostgreSQL
- Pydantic
- Asyncpg
- Docker & Docker Compose
- Cloudinary API
- SMTP for mail (Gmail used in `.env`)

---

## ⚙️ Setup Instructions

### 1. Clone the project

```bash
git clone https://github.com/your-username/goit-pythonweb-hw-10.git
cd goit-pythonweb-hw-10
```

### 2. Configure environment

Create a `.env` file in the root directory with the following content:

```env
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_FROM=your-email@gmail.com
MAIL_PORT=587
MAIL_SERVER=smtp.gmail.com
MAIL_FROM_NAME="My mail app"
MAIL_STARTTLS=True
MAIL_SSL_TLS=False

CLOUDINARY_NAME=your-cloudinary-name
CLOUDINARY_API_KEY=your-cloudinary-api-key
CLOUDINARY_API_SECRET=your-cloudinary-api-secret

DATABASE_URL=db
```

> ⚠️ Use an [App Password](https://support.google.com/accounts/answer/185833?hl=en) for Gmail.

---

### 3. Run with Docker

```bash
docker-compose up --build
```

---

## 📬 API Endpoints

Once running, access the interactive docs:

- Swagger UI: `http://localhost:8000/docs`
- Redoc: `http://localhost:8000/redoc`

Example endpoints:

| Method | Endpoint              | Description            |
|--------|------------------------|------------------------|
| POST   | `/auth/signup`         | Register new user      |
| POST   | `/auth/login`          | Login + get JWT token  |
| GET    | `/contacts/`           | Get all contacts       |
| POST   | `/contacts/`           | Create contact         |
| GET    | `/contacts/search`     | Search by name/email   |
| GET    | `/contacts/birthday`   | Birthdays next 7 days  |
| PATCH  | `/users/avatar`        | Upload avatar to Cloudinary |

---

## 🧪 Run Tests (Optional)

If you want to test outside Docker:

```bash
poetry install
poetry run pytest
```

---

## 📦 Project Structure

```
.
├── docker-compose.yml
├── Dockerfile
├── .env
├── src/
│   ├── api/                # API routers
│   ├── services/           # Business logic
│   ├── repository/         # DB queries
│   ├── database/           # DB models, config
│   ├── conf/               # Settings
│   └── main.py             # App entry
```

---

## 💬 Author

- 🧑‍💻 Dmytro Mayevsky
- ✉️ [mayevskydv@gmail.com](mailto:mayevskydv@gmail.com)

---

## 📜 License

This project is licensed under the MIT License.

