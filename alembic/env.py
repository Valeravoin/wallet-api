import os
import sys
import asyncio
from logging.config import fileConfig
from sqlalchemy import pool, create_engine
from sqlalchemy.ext.asyncio import create_async_engine
from alembic import context

# Подключаем корень проекта
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from app.models import Base
    print("✅ Alembic нашёл модели из app.models")
except ImportError as e:
    print(f"❌ Ошибка импорта моделей: {e}")
    sys.exit(1)

target_metadata = Base.metadata
config = context.config

# Логика выбора URL
database_url = os.getenv("DATABASE_URL")

# Если задана переменная ALEMBIC_ENV_OFFLINE=1 — используем синхронный драйвер для миграций
if os.getenv("ALEMBIC_ENV_OFFLINE") == "1":
    database_url = "postgresql+psycopg2://postgres:postgres@db:5432/wallet_db"
    print("🔧 Режим миграций: синхронный (psycopg2)")
elif not database_url:
    database_url = "postgresql+asyncpg://postgres:postgres@db:5432/wallet_db"
    print("⚡ Режим: асинхронный (asyncpg)")

config.set_main_option("sqlalchemy.url", database_url)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()

async def run_migrations_online():
    connectable = create_async_engine(config.get_main_option("sqlalchemy.url"), echo=False, future=True)
    async with connectable.connect() as connection:
        await connection.run_sync(context.run_migrations)
    await connectable.dispose()

# ГЛАВНАЯ ЛОГИКА: если ALEMBIC_ENV_OFFLINE=1 ИЛИ context.is_offline_mode() — идём синхронно
if context.is_offline_mode() or os.getenv("ALEMBIC_ENV_OFFLINE") == "1":
    print("🚀 Запуск миграций в синхронном режиме (обход ошибки asyncio)...")
    sync_engine = create_engine(
        config.get_main_option("sqlalchemy.url"),
        poolclass=pool.NullPool,
        echo=False
    )
    with sync_engine.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()
else:
    asyncio.run(run_migrations_online())
