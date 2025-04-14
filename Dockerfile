FROM python:3.12-slim

WORKDIR /app


COPY pyproject.toml poetry.lock ./
RUN pip install --upgrade pip && \
    pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-root


COPY . .


CMD ["db:5432", "--", "poetry", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]