from contextlib import asynccontextmanager
from typing import AsyncGenerator

from redis.asyncio import ConnectionPool, Redis

from src.jwt_auth import settings


class RedisConnector:
    def __init__(self):
        self.url = settings.redis.url
        self._pool: ConnectionPool = self._init_pool()

    def _init_pool(self):
        return ConnectionPool.from_url(url=self.url, encoding="utf-8", decode_responses=True)

    @asynccontextmanager
    async def get_client(self) -> AsyncGenerator:
        redis_client = Redis(connection_pool=self._pool)
        try:
            yield redis_client
        finally:
            await redis_client.aclose()
