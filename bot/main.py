from asyncio import run
import logging
import logging.config
from typing import List
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.fsm.storage.base import DefaultKeyBuilder
from aiogram.client.default import DefaultBotProperties
from aiogram import Bot, Dispatcher, Router
from redis.asyncio import Redis

from database.engine import postgres_connect
from handlers._controller.controller import controller
from middlewares.retry_after_middleware import RetryAfterMiddleware
from config_reader import config

async def setup_database() -> None:
    await postgres_connect()

async def setup_routers(dispatcher: Dispatcher) -> None:
    routers: List[Router] = await controller()
    for router in routers:
        dispatcher.include_router(router=router)

async def setup_logging() -> None:
    logging.config.dictConfig(config=config.logging)

async def on_startup(dispatcher: Dispatcher, bot: Bot) -> None:
    await setup_logging()
    await postgres_connect()
    await setup_routers(dispatcher=dispatcher)


async def main() -> None:
    bot: Bot = Bot(token=config.bot.token.get_secret_value(),
              session=RetryAfterMiddleware(limit=config.bot.max_connections),
                default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    storage: RedisStorage = RedisStorage(redis=Redis(host=config.database.redis.dsn.host,
                                                     port=config.database.redis.dsn.port,
                                                     max_connections=config.database.redis.max_connections),
                                                     key_builder=DefaultKeyBuilder(with_destiny=True))
    
    dispatcher: Dispatcher = Dispatcher(bot=bot, storage=storage)
    dispatcher.startup.register(on_startup)

    await dispatcher.start_polling(bot, allowed_updates=dispatcher.resolve_used_update_types())

if __name__ == "__main__":
    run(main())