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


def reminder_time_keyboard():
    keyboard = InlineKeyboardBuilder()
    keyboard.row(
        InlineKeyboardButton(text="За 1 час", callback_data="reminder_1h"),
        InlineKeyboardButton(text="За 4 часа", callback_data="reminder_4h"),
        InlineKeyboardButton(text="За 1 день", callback_data="reminder_1d"),
    )
    keyboard.row(InlineKeyboardButton(text="Не напоминать", callback_data="reminder_none"))
    keyboard.row(InlineKeyboardButton(text="Главное меню", callback_data="back_btn"))
    return keyboard.as_markup()


