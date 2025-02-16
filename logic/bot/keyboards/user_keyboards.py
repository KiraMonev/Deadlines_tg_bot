from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def start_keyboard():
    keyboard = InlineKeyboardBuilder()
    keyboard.row(InlineKeyboardButton(text="Новая запись", callback_data="new_deadline"))
    keyboard.row(InlineKeyboardButton(text="Удалить запись (-и) на число", callback_data="delete_deadlines"),
                 InlineKeyboardButton(text="Просмотр записей", callback_data="show_deadlines"))

    return keyboard.as_markup()
