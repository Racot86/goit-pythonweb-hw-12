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

# 3) (Optional) add wait‑for‑it
ADD https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh /usr/local/bin/wait-for-it.sh
RUN chmod +x /usr/local/bin/wait-for-it.sh

# 4) Tell Docker/Render “we listen on 8000 by default”
ENV PORT=8000
EXPOSE 8000

# 5) At runtime, parse out the real DB host/port and block until it’s ready,
#    then launch Uvicorn on the Render‐provided $PORT
CMD ["bash","-lc","\
  DB_HOST=$(python -c \"import os,urllib.parse as u; print(u.urlparse(os.environ['DATABASE_URL']).hostname)\") && \
  DB_PORT=$(python -c \"import os,urllib.parse as u; print(u.urlparse(os.environ['DATABASE_URL']).port)\") && \
  echo \"⏳ waiting for $PGHOST:$PGPORT…\" && \
  /usr/local/bin/wait-for-it.sh \"$PGHOST:$PGPORT\" --timeout=60 --strict -- \
  uvicorn main:app --host 0.0.0.0 --port ${PORT}\
"]