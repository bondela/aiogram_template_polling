from aiogram.types import Message
from aiogram import html
from handlers.start.keyboard import start_keyboard

async def start(message: Message) -> None:
    await message.reply(text=f"{html.blockquote(value="Bot")}\n\n"
                             f"{html.bold(value=f"Hello, {message.from_user.full_name}")}",
                        reply_markup=start_keyboard(username=message.from_user.username, 
                                                    user_id=message.from_user.id))
