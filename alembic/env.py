
from logging.config import fileConfig
import os

from alembic import context
from sqlalchemy import engine_from_config, pool
from dotenv import load_dotenv

from app.database import Base
from app import models  # Registers Trade, Position and Price models

# Load environment variables from the project's .env file.
load_dotenv()

# Alembic configuration object.
config = context.config

# Configure logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Read the PostgreSQL connection URL from .env.
database_url = os.getenv("DATABASE_URL")

if not database_url:
    raise ValueError("DATABASE_URL is not configured in the .env file")

# Escape percent signs for Alembic's ConfigParser.
config.set_main_option(
    "sqlalchemy.url",
    database_url.replace("%", "%%")
)

# Tell Alembic which SQLAlchemy metadata to inspect.
target_metadata = Base.metadata


def run_migrations_offline():
    """Run migrations without creating a database connection."""

    url = config.get_main_option("sqlalchemy.url")

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations using a live database connection."""

    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()

    connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
