import asyncio
from decimal import Decimal

# --- БАЗОВЫЕ ТЕСТЫ (Простые сценарии) ---


async def test_create_wallet(client):
    """Проверяем, что кошелёк успешно создаётся."""
    payload = {"uuid": "user-test-1", "balance": 100.50}
    response = await client.post("/api/v1/wallets", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["uuid"] == "user-test-1"
    # Используем Decimal для точной проверки денег
    assert Decimal(str(data["balance"])).quantize(Decimal("0.01")) == Decimal("100.50")


async def test_deposit_increases_balance(client):
    """Проверяем, что депозит увеличивает баланс."""
    # 1. Создаём кошелёк
    await client.post("/api/v1/wallets", json={"uuid": "user-test-2", "balance": 0.0})

    # 2. Делаем депозит
    payload = {"operation_type": "deposit", "amount": 50.25}
    response = await client.post("/api/v1/wallets/user-test-2/operation", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert Decimal(str(data["balance"])).quantize(Decimal("0.01")) == Decimal("50.25")


async def test_withdraw_decreases_balance(client):
    """Проверяем, что вывод средств уменьшает баланс."""
    await client.post(
        "/api/v1/wallets", json={"uuid": "user-test-3", "balance": 200.00}
    )

    payload = {"operation_type": "withdraw", "amount": 75.00}
    response = await client.post("/api/v1/wallets/user-test-3/operation", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert Decimal(str(data["balance"])).quantize(Decimal("0.01")) == Decimal("125.00")


async def test_withdraw_insufficient_funds(client):
    """Проверяем защиту от ухода в минус."""
    await client.post("/api/v1/wallets", json={"uuid": "user-test-4", "balance": 10.00})

    payload = {"operation_type": "withdraw", "amount": 100.00}
    response = await client.post("/api/v1/wallets/user-test-4/operation", json=payload)

    assert response.status_code == 400
    assert "Недостаточно средств" in response.text


# --- ТЯЖЁЛЫЙ ТЕСТ (Конкурентность) ---
# Этот тест ставим в самый конец файла. Он самый важный!


async def test_concurrent_withdrawals(client):
    initial_amount = 1000.00
    withdrawal_amount = 10.0
    num_requests = 10
    total_to_withdraw = num_requests * withdrawal_amount

    # 1. Создаём кошелёк
    await client.post(
        "/api/v1/wallets", json={"uuid": "user-concurrent", "balance": initial_amount}
    )

    # 2. Функция-помощник для одного запроса
    async def make_withdrawal(i):
        payload = {"operation_type": "deposit", "amount": withdrawal_amount}
        # ^^^ ВАЖНО: для теста конкурентности лучше делать ОДИНАКОВЫЕ операции.
        # Если у тебя логика "снять" работает только при балансе > 0, то 10 одновременных снятий могут дать race condition.
        # Но если цель — проверить, что баланс не уйдёт в минус из-за гонки, то оставь withdraw.

        # Исправим на withdraw, как у тебя было, но без client.client():
        payload = {"operation_type": "withdraw", "amount": withdrawal_amount}
        resp = await client.post(
            "/api/v1/wallets/user-concurrent/operation", json=payload
        )
        return resp.status_code

    # 3. Запускаем все запросы параллельно
    tasks = [make_withdrawal(i) for i in range(num_requests)]
    results = await asyncio.gather(*tasks)

    # 4. Проверяем, что все запросы прошли успешно (статус 200)
    assert all(status == 200 for status in results), f"Some requests failed: {results}"

    # 5. Проверяем итоговый баланс
    get_resp = await client.get("/api/v1/wallets/user-concurrent")
    final_balance = Decimal(str(get_resp.json()["balance"]))
    expected_balance = Decimal(str(initial_amount - total_to_withdraw))

    assert (
        final_balance == expected_balance
    ), f"Balance mismatch! Expected {expected_balance}, got {final_balance}. Race condition detected!"
