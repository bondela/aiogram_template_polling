import logging
from asyncio import sleep
from time import sleep as global_sleep
from typing import Optional

from aiogram import Bot
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.exceptions import (
    RestartingTelegram,
    TelegramRetryAfter,
    TelegramServerError,
)
from aiogram.methods.base import TelegramMethod, TelegramType


class RetryAfterMiddleware(AiohttpSession):
    async def __call__(
            self,
            bot: Bot,
            method: TelegramMethod[TelegramType],
            timeout: Optional[int] = None,
            sleep_time: Optional[int] = 60,
    ) -> TelegramType:
        while True:
            try:
                return await super().make_request(bot=bot, method=method, timeout=timeout)

            except TelegramRetryAfter as exception:
                logging.warning(f"Retry after exception, sleep for {exception.retry_after}")
                await sleep(exception.retry_after)
                continue

            except (TelegramServerError, RestartingTelegram):
                logging.CRITICAL(f"Interval Telegram error, global sleep for {sleep_time} seconds")
                global_sleep(sleep_time)
                continue

            except Exception:
                raise
            