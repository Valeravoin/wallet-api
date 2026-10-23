import pytest
import asyncpg
from httpx import AsyncClient
import asyncio

# Подключаемся к той же базе, что и приложение, чтобы тесты ходили в реальный Docker-контейнер
DB_URL = "postgresql+asyncpg://postgres:postgres@db:5432/wallet_db"


@pytest.fixture(scope="function")
async def clean_db():
    """Перед каждым тестом полностью очищает таблицу wallets."""
    # Подключаемся напрямую через asyncpg (быстрее и проще для очистки)
    conn = await asyncpg.connect(
        host="db", port=5432, user="postgres", password="postgres", database="wallet_db"
    )
    try:
        await conn.execute("TRUNCATE TABLE wallets RESTART IDENTITY;")
        yield  # Здесь выполняется сам тест
    finally:
        # Можно снова очистить, если тест оставил мусор, но TRUNCATE в начале обычно хватает
        await conn.close()


@pytest.fixture
async def client(clean_db):
    """Создаёт HTTP-клиент."""
    # ВАЖНО: Используем 'app', а не 'localhost'. 
    # В сети Docker имя сервиса 'app' резолвится в IP работающего контейнера.
    async with AsyncClient(base_url="http://app:8000", timeout=10.0) as c:
        
        # Даём приложению 3 секунды на полную инициализацию после старта
        await asyncio.sleep(3)
        
        yield c
