import os
import sys
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from app.models import Base
target_metadata = Base.metadata

config = context.config
database_url = os.getenv("DATABASE_URL", "postgresql+psycopg2://postgres:postgres@db:5432/wallet_db")
# Важно: используем psycopg2 (синхронный), а не asyncpg, чтобы избежать ошибки greenlet/async
config.set_main_option("sqlalchemy.url", database_url.replace("asyncpg", "psycopg2"))

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

if __name__ == "__main__":
    run_migrations_offline()
