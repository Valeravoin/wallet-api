from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app import schemas, repository, models
from app.database import get_db

app = FastAPI()


@app.get("/")
def read_root():
    return {"message": "Wallet API (Async + Locking) is running"}


@app.post("/api/v1/wallets", response_model=schemas.WalletResponse)
async def create_wallet_endpoint(
    wallet_data: schemas.WalletCreate, db: AsyncSession = Depends(get_db)
):
    # Для создания можно оставить простую проверку или усложнить с блокировкой
    existing = await repository.get_wallet_by_uuid_locked(db, wallet_data.uuid)
    if existing:
        raise HTTPException(status_code=400, detail="Кошелёк уже существует")
    return await repository.create_wallet(db, wallet_data)


@app.get("/api/v1/wallets/{uuid}", response_model=schemas.BalanceResponse)
async def get_wallet_balance(uuid: str, db: AsyncSession = Depends(get_db)):
    # Чтение без блокировки (FOR UPDATE не нужен, если мы просто смотрим баланс)
    stmt = select(models.Wallet).where(models.Wallet.uuid == uuid)
    result = await db.execute(stmt)
    wallet = result.scalar_one_or_none()

    if not wallet:
        raise HTTPException(status_code=404, detail="Кошелёк не найден")

    return schemas.BalanceResponse(uuid=wallet.uuid, balance=wallet.balance)


@app.post("/api/v1/wallets/{uuid}/operation", response_model=schemas.BalanceResponse)
async def perform_operation(
    uuid: str, operation: schemas.OperationRequest, db: AsyncSession = Depends(get_db)
):
    """
    Этот эндпоинт теперь гарантированно атомарный благодаря FOR UPDATE.
    """
    return await repository.update_balance(
        db, uuid, operation.operation_type, operation.amount
    )
