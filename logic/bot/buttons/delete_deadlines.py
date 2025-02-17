from aiogram import F, Router, types

from logic.bot.keyboards.user_keyboards import back_keyboard

router = Router()


@router.callback_query(F.data == "delete_deadlines")
async def delete_deadlines_button(callback_query: types.CallbackQuery):
    await callback_query.message.edit_text("Вы выбрали 'Удаление записей'\n\n"
                                           "Введите дату, с которой нужно удалить все дедлайны",
                                           reply_markup=back_keyboard())
