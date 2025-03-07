from aiogram import Router
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message

from logic.bot.keyboards.user_keyboards import start_keyboard

router = Router()


@router.message(Command("start"))
async def start_command(message: Message):
    user_name = str(message.from_user.username)
    user_id = str(message.from_user.id)

    # реализовать сохранение в БД

    await message.answer(
        "👋 <b>Привет!</b> Я — твой личный помощник по дедлайнам! ⏳\n\n"
        "🔽 Выбери действие ниже и начнём! 🔽",
        reply_markup=start_keyboard(),
        parse_mode=ParseMode.HTML
    )
