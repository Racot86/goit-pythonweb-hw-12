FROM python:3.12-slim
WORKDIR /app

# 1) Copy only the pyproject and lock so that Docker can cache deps
COPY pyproject.toml poetry.lock ./

# 2) Install Poetry, then your deps (this layer will invalidate once lockfile changes)
RUN pip install --upgrade pip \
 && pip install poetry \
 && poetry config virtualenvs.create false \
 && poetry install --no-root

# 3) Now copy the rest of your code
COPY . .

# 4) Run
CMD ["poetry", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "$PORT"]