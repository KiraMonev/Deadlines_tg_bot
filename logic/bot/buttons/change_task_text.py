from datetime import datetime, timedelta, timezone

from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext

from logic.bot.keyboards.user_keyboards import (back_keyboard,
                                                task_manager_keyboard)
from logic.bot.states.UserStates import UserState
from logic.db.database import db

router = Router()


@router.callback_query(F.data == "change_text")
async def change_text_button(callback_query: types.CallbackQuery, state: FSMContext):
    await state.set_state(UserState.TASK_CHANGE_TEXT)

    message_text = "Назначьте новый текст этой задаче"

    await callback_query.message.edit_text(message_text, reply_markup=back_keyboard())


@router.message(F.text, UserState.TASK_CHANGE_TEXT)
async def exchange_text(message: types.Message, state: FSMContext):
    new_text = message.text
    data = await state.get_data()
    await state.clear()
    task_id = data["current_data"]["_id"]

    cur_data = dict()
    cur_data["current_data"] = await db.get_task(task_id)

    deadline_date = cur_data["current_data"]["deadline_date"]
    deadline_time = cur_data["current_data"]["deadline_time"]
    is_completed = "Да" if cur_data["current_data"]["is_completed"] else "Нет"
    created_at = cur_data["current_data"]["created_at"].strftime("%Y-%m-%d %H:%M")
    updated_at = datetime.now(timezone(timedelta(hours=3))).strftime("%Y-%m-%d %H:%M")

    message_text = (
        f"Задача: {new_text}\n\n"
        f"Дедлайн: {deadline_date} {deadline_time}\n"
        f"Выполнено: {is_completed}\n"
        f"Создана: {created_at}\n"
        f"Обновлена: {updated_at}"
    )

    try:
        await db.update_task_details(task_id=task_id, new_text=new_text)
    except Exception as e:
        await message.answer("Произошла ошибка с сохранением нового текста")
    finally:
        await message.answer(message_text, reply_markup=task_manager_keyboard())
        new_data = dict()
        new_data["current_data"] = await db.get_task(task_id)
        await state.set_state(UserState.TASK_MANAGEMENT)
        await state.set_data(new_data)
