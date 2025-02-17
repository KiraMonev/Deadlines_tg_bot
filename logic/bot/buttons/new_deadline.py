from aiogram import F, Router, types

from logic.bot.keyboards.user_keyboards import back_keyboard

router = Router()


@router.callback_query(F.data == "new_deadline")
async def new_deadline_button(callback_query: types.CallbackQuery):
    await callback_query.message.edit_text("Вы выбрали 'Добавление новой записи'\n\n"
                                           "Введите текст задачи и дату, когда она должна быть выполнена",
                                           reply_markup=back_keyboard())
