from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData

class StartCallback(CallbackData, prefix="start"):
    user_id: int

def start_keyboard(username: str, user_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for _ in range(3):
        builder.button(text=f"Привет, {username}", callback_data=StartCallback(user_id=user_id))

    builder.adjust(1)
    return builder.as_markup()