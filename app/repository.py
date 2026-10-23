from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from app import models, schemas
from fastapi import HTTPException
from decimal import Decimal


# --- Асинхронная функция поиска с блокировкой ---
async def get_wallet_by_uuid_locked(
    db: AsyncSession, uuid: str
) -> models.Wallet | None:
    """
    Находит кошелёк и ставит блокировку на строку (FOR UPDATE).
    Пока эта транзакция не завершится (commit/rollback), другие запросы
    на этот uuid будут ждать.
    """
    stmt = select(models.Wallet).where(models.Wallet.uuid == uuid).with_for_update()
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def create_wallet(
    db: AsyncSession, wallet_data: schemas.WalletCreate
) -> models.Wallet:
    # В реальной системе тут тоже нужна проверка на существование с блокировкой,
    # но для простоты оставим как есть, так как UUID уникален на уровне БД или проверяется отдельно.
    balance_val = Decimal(str(wallet_data.balance))
    db_wallet = models.Wallet(uuid=wallet_data.uuid, balance=balance_val)
    db.add(db_wallet)
    await db.commit()
    await db.refresh(db_wallet)
    return db_wallet


async def update_balance(
    db: AsyncSession, uuid: str, operation_type: str, amount: Decimal
) -> schemas.BalanceResponse:
    """
    Атомарная операция с блокировкой строки.
    """
    # 1. Получаем кошелёк С БЛОКИРОВКОЙ.
    # Если другой запрос уже заблокировал эту строку, этот запрос встанет в очередь здесь.
    wallet = await get_wallet_by_uuid_locked(db, uuid)

    if not wallet:
        raise HTTPException(status_code=404, detail="Кошелёк не найден")

    current_balance = Decimal(str(wallet.balance))

    # 2. Логика проверки и изменения (происходит в памяти, но строка в БД заблокирована!)
    if operation_type == "deposit":
        new_balance = current_balance + amount
    elif operation_type == "withdraw":
        if current_balance < amount:
            # Даже если кто-то успел списать деньги до этой проверки,
            # мы не могли прочитать баланс, пока не получили блокировку.
            # Но если баланс < amount, значит денег реально нет.
            raise HTTPException(status_code=400, detail="Недостаточно средств")
        new_balance = current_balance - amount
    else:
        raise HTTPException(status_code=400, detail="Неверный тип операции")

    # 3. Обновляем объект
    wallet.balance = new_balance

    # 4. Сохраняем изменения.
    # Блокировка снимется автоматически после commit (или rollback).
    await db.commit()
    await db.refresh(wallet)

    return schemas.BalanceResponse(
        uuid=wallet.uuid, balance=wallet.balance, last_operation=operation_type
    )
