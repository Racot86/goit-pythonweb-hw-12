from logging.config import fileConfig
from pathlib import Path
import asyncio

from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context

# ─── наше сховище налаштувань ───
from src.conf.config import settings
from src.database.models import Base  # містить metadata

# ─── базова конфігурація Alembic ───
config = context.config
fileConfig(config.config_file_name)

# завжди використовуємо URL із settings, а не з ini
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

target_metadata = Base.metadata


# ────────────────────────────────────────────────
# OFFLINE
# ────────────────────────────────────────────────
def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = settings.DATABASE_URL
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


# ────────────────────────────────────────────────
# ONLINE (async)
# ────────────────────────────────────────────────
def run_migrations_online() -> None:
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        future=True,
    )

    def do_run_migrations(connection):
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )
        with context.begin_transaction():
            context.run_migrations()

    async def do_migrations():
        async with connectable.connect() as connection:
            await connection.run_sync(do_run_migrations)   # ← обёртка, не context.run_migrations

    asyncio.run(do_migrations())


# ────────────────────────────────────────────────
# DELEGATE TO ONE OR THE OTHER
# ────────────────────────────────────────────────
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()