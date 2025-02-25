import logging
import logging.config
from asyncio import run
from typing import List
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.fsm.storage.base import DefaultKeyBuilder
from aiogram.client.default import DefaultBotProperties
from aiogram.client.telegram import TelegramAPIServer
from aiogram import Bot, Dispatcher, Router
from redis.asyncio import Redis
from aiohttp import web

from config_reader import config
from database.engine import postgres_connect, database_session
from middlewares.database_middleware import DatabaseMiddleware
from middlewares.retry_after_middleware import RetryAfterMiddleware
from middlewares.user_middleware import UserMiddleware
from handlers._controller.controller import controller

async def setup_logging() -> None:
    logging.config.dictConfig(config=config.logging)

async def setup_database() -> None:
    await postgres_connect()

async def setup_middlewares(dispatcher: Dispatcher) -> None:
    for middleware in [DatabaseMiddleware(session=database_session), UserMiddleware()]:
        dispatcher.update.outer_middleware(middleware=middleware)

async def setup_routers(dispatcher: Dispatcher) -> None:
    routers: List[Router] = await controller()
    for router in routers:
        dispatcher.include_router(router=router)

async def on_startup(dispatcher: Dispatcher, bot: Bot) -> None:
    await setup_logging()
    await setup_database()
    await setup_middlewares(dispatcher=dispatcher)
    await setup_routers(dispatcher=dispatcher)

async def main() -> None:
    if not config.bot.local_api:
        session = RetryAfterMiddleware(limit=config.bot.max_connections)
    else:
        session = RetryAfterMiddleware(
            api=TelegramAPIServer.from_base(base=config.bot.local_base),
            limit=config.bot.max_connections
        )

    bot = Bot(
        token=config.bot.token.get_secret_value(),
        session=session,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )

    storage = RedisStorage(
        redis=Redis(
            host=config.database.redis.dsn.host,
            port=config.database.redis.dsn.port,
            max_connections=config.database.redis.max_connections
        ),
        key_builder=DefaultKeyBuilder(with_destiny=True)
    )
    dispatcher: Dispatcher = Dispatcher(bot=bot, storage=storage)
    dispatcher.startup.register(on_startup)
    await dispatcher.start_polling(bot, allowed_updates=dispatcher.resolve_used_update_types())

if __name__ == "__main__":
    run(main())