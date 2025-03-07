import logging

from aiogram import Bot
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def start_keyboard():
    keyboard = InlineKeyboardBuilder()
    keyboard.row(InlineKeyboardButton(text="Новая запись", callback_data="new_deadline"))
    keyboard.row(InlineKeyboardButton(text="Удалить запись (-и) на число", callback_data="delete_deadlines"),
                 InlineKeyboardButton(text="Просмотр записей", callback_data="show_deadlines"))

    return keyboard.as_markup()


def task_manager_keyboard():
    keyboard = InlineKeyboardBuilder()
    keyboard.row(InlineKeyboardButton(text="Изменить текст", callback_data="change_text"),
                 InlineKeyboardButton(text="Изменить дедлайн", callback_data="change_deadline"))
    keyboard.row(InlineKeyboardButton(text="Поставить галочку о выполнении", callback_data="tick_task"))
    keyboard.row(InlineKeyboardButton(text="Удалить задачу", callback_data="delete_task"))
    keyboard.row(InlineKeyboardButton(text="Главное меню", callback_data="back_btn"))
    return keyboard.as_markup()


def back_keyboard():
    keyboard = InlineKeyboardBuilder()
    keyboard.row(InlineKeyboardButton(text="Главное меню", callback_data="back_btn"))
    return keyboard.as_markup()


async def remove_keyboard(bot: Bot, chat_id: int, message_id: int) -> None:
    try:
        await bot.edit_message_reply_markup(
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=None
        )
    except Exception as e:
        logging.error(e)
