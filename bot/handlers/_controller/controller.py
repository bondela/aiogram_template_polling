from typing import List
from aiogram import Router

from handlers._controller.routers.user import user_router


async def controller() -> List[Router]:
    user: Router = await user_router()

    return [user]