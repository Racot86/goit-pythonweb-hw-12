# Dockerfile
FROM python:3.12-slim

# ensure Python output is sent straight to the terminal (no buffering)
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# install system deps & Poetry, then your Python deps
COPY pyproject.toml poetry.lock ./
RUN pip install --upgrade pip \
    && pip install poetry \
    && poetry config virtualenvs.create false \
    && poetry install --no-root

# copy the rest of your code
COPY . .

# expose the port (optional in Docker, but documents intent)
EXPOSE 8000

# shell form CMD so $PORT is expanded by /bin/sh
# fall back to 8000 locally if PORT isn't set
CMD poetry run uvicorn main:app \
    --host 0.0.0.0 \
    --port ${PORT:-8000}