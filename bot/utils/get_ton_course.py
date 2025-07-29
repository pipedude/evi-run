from aiohttp import ClientSession

from redis.asyncio.client import Redis

url = "https://api.coingecko.com/api/v3/simple/price"


async def get_ton_course(redis: Redis):
    ton_price = await redis.get("ton_price")
    if ton_price:
        return ton_price

    params = {
        "ids": "the-open-network",
        "vs_currencies": "usd"
    }
    async with ClientSession() as session:
        async with session.get(url, ssl=False, params=params) as response:
            try:
                data = await response.json()
                ton_price = data["the-open-network"]["usd"]
                await redis.set("ton_price", ton_price, ex=5)
                return ton_price
            except Exception as e:
                return
