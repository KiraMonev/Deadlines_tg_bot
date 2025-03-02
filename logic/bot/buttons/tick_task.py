from datetime import datetime, timedelta, timezone

from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext

from logic.bot.keyboards.user_keyboards import task_manager_keyboard
from logic.db.database import db

router = Router()


@router.callback_query(F.data == "tick_task")
async def tick_task_button(callback_query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    task_id = data["current_data"]["_id"]
    await db.mark_task_completed(task_id)

    deadline_date = data["current_data"]["deadline_date"]
    deadline_time = data["current_data"]["deadline_time"]
    previous_status = data["current_data"]["is_completed"]
    is_completed = "Да"
    # reminder_date = task["reminder_date"]
    # reminder_time = task["reminder_time"]
    created_at = data["current_data"]["created_at"].strftime("%Y-%m-%d %H:%M")
    updated_at = datetime.now(timezone(timedelta(hours=3))).strftime("%Y-%m-%d %H:%M")
    text = data["current_data"]["text"]

    if previous_status == "Да":
        await callback_query.answer()
    else:
        message_text = (
            f"Задача: {text}\n\n"
            f"Дедлайн: {deadline_date} {deadline_time}\n"
            f"Выполнено: {is_completed}\n"
            f"Создана: {created_at}\n"
            f"Обновлена: {updated_at}"
        )

        await db.mark_task_completed(task_id)
        await callback_query.message.edit_text(message_text, reply_markup=task_manager_keyboard())
