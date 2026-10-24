# Wallet API 💼

Асинхронный сервис для управления кошельками на FastAPI + SQLAlchemy + PostgreSQL.  
Проект полностью упакован в Docker Compose, настроен CI‑ready стиль кода (black/flake8), миграции (Alembic) и базовая защита от конкурентности.

---

## Стек технологий 🧰

- **Язык и фреймворк:** Python 3.11, FastAPI ⚡
- **ORM и миграции:** SQLAlchemy 2.0 (async), Alembic 📜
- **База данных:** PostgreSQL (в Docker) 🗄️
- **Контейнеризация:** Docker, Docker Compose 🐳
- **Тестирование:** pytest, pytest-asyncio, httpx 🧪
- **Стиль кода:** black (форматирование), flake8 (линтинг) ✨
- **Переменные окружения:** python-dotenv 🔑

---

## Подготовка к запуску 🔧

1. **Клонируй репозиторий:**
   ```bash
   git clone <ссылка-на-репозиторий>
   cd wallet-api

2. **Настрой переменные окружения:**
   ```bash
   cp .env.example .env

## Как запустить проект 🚀

1. **Подними инфраструктуру (база данных + приложение):**
   ```bash
   docker compose up -d --build

2. **Проверь, что сервисы запущены:**
   ```bash
   docker compose ps
   Убедись, что статусы app и db — Up.

## Работа с миграциями 🛠️

**Почему так: Alembic — синхронный инструмент. Для применения миграций мы используем синхронный драйвер psycopg2, а приложение продолжает работать на asyncpg. Переменная ALEMBIC_ENV_OFFLINE=1 переключает подключение внутри alembic/env.py.**

1. **Применить все миграции:**
   ```bash
   docker compose run --rm -e ALEMBIC_ENV_OFFLINE=1 app alembic upgrade head

2. **Создать новую миграцию (автоматически):**
   ```bash
   docker compose run --rm app alembic revision --autogenerate -m "add_transactions_table"

3. **Откатить последнюю миграцию:**
   ```bash
   docker compose run --rm -e ALEMBIC_ENV_OFFLINE=1 app alembic downgrade -1

4. **Проверить статус миграций:**
   ```bash
   docker compose exec db psql -U postgres -d wallet_db -c "SELECT * FROM alembic_version;"

## Тестирование 🧫

**Тесты изолированы и очищают базу перед каждым запуском.**

1. **Убедись, что стек поднят:**
   ```bash
   docker compose up -d

2. **Запусти тесты:**
   ```bash
   docker compose run --rm app pytest tests/ -v

3. **Ожидаемый результат:**
   ```bash
   5 passed in ...s
  💡 Совет: Если тесты падают с ConnectError, убедись, что команда up -d была выполнена перед запуском тестов. Контейнер app должен быть запущен, чтобы тесты могли постучаться в него по имени сервиса.

## Проверка данных в базе 👁️

1. **Чтобы посмотреть текущие кошельки напрямую в PostgreSQL:**
   ```bash
   docker compose exec db psql -U postgres -d wallet_db -c "SELECT uuid, balance, created_at FROM wallets;"
