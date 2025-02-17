from aiogram import F, Router, types

from logic.bot.keyboards.user_keyboards import back_keyboard

router = Router()


@router.callback_query(F.data == "show_deadlines")
async def show_deadline_button(callback_query: types.CallbackQuery):
    await callback_query.message.edit_text("Вы выбрали 'Просмотр всех записей'",
                                           reply_markup=back_keyboard())
