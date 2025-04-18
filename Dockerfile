FROM python:3.12-slim

WORKDIR /app

# 1) Install your deps
COPY pyproject.toml poetry.lock ./
RUN pip install --upgrade pip \
 && pip install poetry \
 && poetry config virtualenvs.create false \
 && poetry install --no-root

# 2) Copy your code
COPY . .

# 3) (Optional) add wait‑for‑it so you don’t race the DB
ADD https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh /usr/local/bin/wait-for-it.sh
RUN chmod +x /usr/local/bin/wait-for-it.sh

# 4) Tell Docker (and Render) which port we plan to listen on by default
#    Render will still set $PORT to e.g. 10000 at runtime,
#    but this EXPOSE makes the scanner happy.
ENV PORT=8000
EXPOSE 8000

# 5) Finally, in CMD we parse out the real host/port from $DATABASE_URL,
#    wait for Postgres, then launch Uvicorn on $PORT
CMD ["sh","-c","\
    host=$(echo $DATABASE_URL | sed -E 's|.*@([^:/]+):.*|\\1|') && \
    port=$(echo $DATABASE_URL | sed -E 's|.*:([0-9]+)/.*|\\1|') && \
    /usr/local/bin/wait-for-it.sh \"$host:$port\" --timeout=30 -- \
    uvicorn main:app --host 0.0.0.0 --port ${PORT}\
"]