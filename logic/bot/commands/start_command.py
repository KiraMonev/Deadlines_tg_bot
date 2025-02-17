from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from logic.bot.keyboards.user_keyboards import start_keyboard

router = Router()


@router.message(Command("start"))
async def start_command(message: Message):
    user_name = str(message.from_user.username)
    user_id = str(message.from_user.id)

    # реализовать сохранение в БД

    await message.answer(f"Привет! Я - твой помощник в отслеживании дедлайнов!\n\n"
                         f"Выбери из списка то, что хочешь сделать и начнём", reply_markup=start_keyboard())
