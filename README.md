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

## Структура проекта 📂

Основные компоненты внутри папки app:

- main.py — точка входа, инициализация FastAPI‑приложения.
- models.py — SQLAlchemy‑модели (ORM), описывают структуру таблиц (например, Wallet).
- schemas.py — Pydantic‑модели, валидируют входные и выходные данные API.
- repository.py — слой доступа к данным (CRUD‑операции с базой).
- database.py — настройка асинхронной сессии и движка (AsyncSession, create_async_engine).

---

## Работа с миграциями 🛠️

**Из‑за асинхронной природы проекта (SQLAlchemy 2.0 + `asyncpg`) миграции Alembic выполняются в синхронном режиме.**
- Применить все миграции: docker compose run --rm -e ALEMBIC_ENV_OFFLINE=1 app alembic upgrade head
- Когда нужно добавить новую таблицу или поле: docker compose run --rm app alembic revision -m "add_transactions_table". После этого отредактируй созданный файл в папке alembic/versions, добавив логику в upgrade() и downgrade().
- Откатить последнюю миграцию: docker compose run --rm -e ALEMBIC_ENV_OFFLINE=1 app alembic downgrade -1
- Откатить до конкретной версии: docker compose run --rm -e ALEMBIC_ENV_OFFLINE=1 app alembic downgrade <revision_id>

## Тестирование 🧫

**Чтобы запустить тесты:**
- Команда для установки пакетов: docker compose up -d --build
- Команда для запуска тестов: docker compose run --rm app pytest tests/ -v
Проект настроен на использование pytest-asyncio, поэтому асинхронные тесты выполняются корректно.

## Как запустить 🚀

1. **Убедись, что есть файл `.env`** в корне проекта (пример `.env.example` можно создать вручную).  
   Обязательные переменные:
   ```env
   DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/wallet_db
   DEBUG=true
