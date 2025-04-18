FROM python:3.12-slim

# 1) Install build‑deps for psycopg2
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
       gcc \
       libpq-dev \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 2) Copy poetry files and install dependencies
COPY pyproject.toml poetry.lock ./
RUN pip install --upgrade pip \
 && pip install poetry \
 && poetry config virtualenvs.create false \
 && poetry install --no-root

# 3) In case psycopg2‑binary isn't in your pyproject, install it here
RUN pip install psycopg2-binary

# 4) Copy the rest of your code
COPY . .

# 5) Launch Uvicorn, using $PORT from Render or defaulting to 8000
CMD ["sh", "-c", "poetry run uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000} --reload"]