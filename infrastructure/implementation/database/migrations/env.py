import asyncio
import pathlib
from logging.config import fileConfig

from alembic import context
from dynaconf import Dynaconf
from sqlalchemy import engine_from_config, pool
from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import AsyncEngine

from infrastructure.implementation.database.orm import tables

config = context.config
fileConfig(config.config_file_name)
target_metadata = tables.mapper_registry.metadata

BASE_DIR = pathlib.Path(__name__).resolve().parent.parent.parent.parent.parent

project_settings = Dynaconf(
    settings_files=["settings.toml", ".secrets.toml"],
    preload=[BASE_DIR / "settings.toml"],
    environments=["development", "production", "testing"],
    auto_cast=True,
)

config.set_main_option(
    "sqlalchemy.url",
    str(
        URL.create(
            drivername="postgresql+asyncpg",
            username=project_settings.db.user,
            password=project_settings.db.password,
            host=project_settings.db.host,
            database=project_settings.db.database,
        )
    ),
)


def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = AsyncEngine(
        engine_from_config(
            config.get_section(config.config_ini_section),
            prefix="sqlalchemy.",
            poolclass=pool.NullPool,
            future=True,
        )
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
