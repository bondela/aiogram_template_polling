from datetime import datetime, timedelta
from typing import Dict, Any, Callable, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from aiogram_i18n import I18nMiddleware
from aiogram_i18n.managers import BaseManager
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import User

class UserManager(BaseManager):
    async def set_locale(self, locale: str, user: User, database: AsyncSession) -> None:
        user.language = locale
        await database.commit()

    async def get_locale(self, user: User) -> str:
        return user.language
    
class UserMiddleware(BaseMiddleware):
    def __init__(self, i18n_middleware: I18nMiddleware):
        self.i18n_middleware = i18n_middleware

    async def __call__(self,
                       handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
                       event: TelegramObject,
                       data: Dict[str, Any]) -> Any:
        event_user: TelegramObject = data["event_from_user"]
        database: AsyncSession = data["database"]

        user_object: User | None = await database.get(entity=User, ident=event_user.id)

        if not user_object:
            user_object = User(id=event_user.id, username=event_user.username, language=event_user.language_code)
            database.add(user_object)
        else:
            if datetime.now() - user_object.last_activity > timedelta(minutes=1):
                user_object.last_activity = datetime.now()
            if user_object.username != event_user.username:
                user_object.username = event_user.username
            if user_object.language != event_user.language_code:
                user_object.language = event_user.language_code

        await database.merge(user_object)
        await database.commit()

        data["user"] = user_object
        return await handler(event, data)