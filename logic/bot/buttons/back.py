from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext

from logic.bot.keyboards.user_keyboards import start_keyboard

router = Router()


@router.callback_query(F.data == "back_btn")
async def back_button(callback_query: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback_query.message.edit_text(
        "👋 <b>Привет!</b> Я — твой личный помощник по дедлайнам! ⏳\n\n"
        "🔽 Выбери действие ниже и начнём! 🔽",
        reply_markup=start_keyboard(),
    )
