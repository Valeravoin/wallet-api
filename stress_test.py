import asyncio
import aiohttp
import time

URL = "http://localhost:8000/api/v1/wallets/user-124/operation"
PAYLOAD = {
    "operation_type": "withdraw",
    "amount": 10.00
}

async def make_request(session, i):
    try:
        async with session.post(URL, json=PAYLOAD) as resp:
            data = await resp.json()
            print(f"Request {i}: Status {resp.status}, Balance: {data.get('balance')}")
            return resp.status
    except Exception as e:
        print(f"Request {i} failed: {e}")
        return None

async def main():
    print("Starting 10 concurrent withdrawals of 10.00 each...")
    start_time = time.time()
    
    async with aiohttp.ClientSession() as session:
        # Создаем 10 задач одновременно
        tasks = [make_request(session, i) for i in range(10)]
        results = await asyncio.gather(*tasks)
        
    end_time = time.time()
    print(f"Finished in {end_time - start_time:.2f} seconds")
    print(f"Successful requests: {sum(1 for r in results if r == 200)}")

if __name__ == "__main__":
    asyncio.run(main())
