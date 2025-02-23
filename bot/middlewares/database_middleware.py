from typing import Callable, Awaitable, Dict, Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from redis import Redis
from config_reader import Config, get_config
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from database.engine import redis_client

class DatabaseMiddleware(BaseMiddleware):
    def __init__(self, session: async_sessionmaker):
        super().__init__()
        self.session: AsyncSession = session
        self.redis_client: Redis = redis_client
        self.config: Config = get_config()

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:
        data["config"] = self.config
        data["redis"] = self.redis_client
        async with self.session() as session:
            data["database"] = session
            return await handler(event, data)