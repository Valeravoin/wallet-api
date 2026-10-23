from decimal import Decimal
from pydantic import BaseModel, Field
from typing import Literal


# --- 1. Для создания кошелька ---
class WalletCreate(BaseModel):
    """
    Схема для создания кошелька: какие данные клиент обязан прислать.
    Используется как входной DTO (Data Transfer Object).
    """

    uuid: str  # Уникальный идентификатор кошелька (строка)

    # Баланс по умолчанию 0.00, если клиент не прислал значение.
    # Decimal нужен для точных расчётов без ошибок округления (никаких float!).
    balance: Decimal = Field(default=Decimal("0.00"))


class WalletResponse(BaseModel):
    """
    Схема ответа при создании кошелька.
    Возвращается клиенту после успешного создания.
    """

    uuid: str
    balance: Decimal

    class Config:
        # Ключевой момент: позволяет Pydantic брать данные из SQLAlchemy-объекта (ORM).
        # Иначе пришлось бы вручную писать: {"uuid": wallet.uuid, "balance": wallet.balance}
        from_attributes = True


# --- 2. Для операции над балансом ---
# Literal ограничивает возможные значения: операция может быть ТОЛЬКО "deposit" или "withdraw".
# Если клиент пришлёт "buy" или "transfer" — Pydantic сразу вернёт ошибку 422.
OperationType = Literal["deposit", "withdraw"]


class OperationRequest(BaseModel):
    """
    Запрос на операцию: тип и сумма.
    Здесь происходит жёсткая валидация входных данных ДО попадания в бизнес-логику.
    """

    operation_type: OperationType  # Только разрешённые типы операций

    # amount > 0: нельзя передать 0 или отрицательную сумму.
    # gt = greater than (больше чем). Decimal('0') — безопасная проверка для денег.
    amount: Decimal = Field(gt=Decimal("0"))


class BalanceResponse(BaseModel):
    """
    Ответ после операции: текущий баланс и тип последней операции.
    """

    uuid: str
    balance: Decimal
    last_operation: str | None = None  # Может быть None, если операций ещё не было

    class Config:
        # Позволяет брать данные из ORM-объекта, даже если у него есть дополнительные поля.
        # Pydantic сам отфильтрует лишнее и оставит только uuid, balance, last_operation.
        from_attributes = True
