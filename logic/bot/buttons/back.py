from aiogram import F, Router, types

from logic.bot.keyboards.user_keyboards import start_keyboard

router = Router()


@router.callback_query(F.data == "back_btn")
async def back_button(callback_query: types.CallbackQuery):
    await callback_query.message.edit_text(f"Привет! Я - твой помощник в отслеживании дедлайнов!\n\n"
                                           f"Выбери из списка то, что хочешь сделать и начнём",
                                           reply_markup=start_keyboard())
