from aiogram import Router
from aiogram.filters.command import CommandStart

from handlers.start.start import start

async def user_router() -> Router:
    router: Router = Router()

    router.message.register(
        start,
        CommandStart()
    )
    
    return router