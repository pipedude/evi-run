import os

from dotenv import load_dotenv
from redis.asyncio.client import Redis

load_dotenv()

redis = Redis.from_url(os.getenv('REDIS_URL'), decode_responses=True)