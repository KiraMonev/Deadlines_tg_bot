from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext

from logic.bot.keyboards.user_keyboards import back_keyboard
from logic.db.database import db

router = Router()


@router.callback_query(F.data == "delete_task")
async def delete_task_button(callback_query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    task_id = data["current_data"]["_id"]
    await db.delete_task(task_id)

    message_text = "Задача удалена"

    await callback_query.message.edit_text(message_text, reply_markup=back_keyboard())
