FROM python:3.12-slim

WORKDIR /app

# 1) Install dependencies
COPY pyproject.toml poetry.lock ./
RUN pip install --upgrade pip \
 && pip install poetry \
 && poetry config virtualenvs.create false \
 && poetry install --no-root

# 2) Copy your code
COPY . .

# 5) At runtime, parse out the real DB host/port and block until it’s ready,
#    then launch Uvicorn on the Render‐provided $PORT
CMD ["sh", "-c", "poetry run uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000} --reload"]