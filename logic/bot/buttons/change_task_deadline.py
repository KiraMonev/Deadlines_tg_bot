from datetime import datetime

from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext

from logic.bot.keyboards.user_keyboards import (back_keyboard,
                                                task_manager_keyboard)
from logic.bot.states.UserStates import UserState
from logic.db.database import db

router = Router()


@router.callback_query(F.data == "change_deadline")
async def change_deadline_button(callback_query: types.CallbackQuery, state: FSMContext):
    await state.set_state(UserState.TASK_CHANGE_DATE)

    message_text = "Назначьте новую дату этой задаче"

    await callback_query.message.edit_text(message_text, reply_markup=back_keyboard())


@router.message(F.text, UserState.TASK_CHANGE_DATE)
async def exchange_deadline_date(message: types.Message, state: FSMContext):
    new_deadline_date = message.text
    data = await state.get_data()
    await state.clear()
    data['current_data']['deadline_date'] = new_deadline_date

    message_text = (f"Новая дата для дедлайна: {new_deadline_date}\n\n"
                    f"Введите новое время для дедлайна")

    await message.answer(message_text)
    await state.set_state(UserState.TASK_CHANGE_TIME)
    await state.set_data(data)


@router.message(F.text, UserState.TASK_CHANGE_TIME)
async def exchange_deadline_time(message: types.Message, state: FSMContext):
    new_deadline_time = message.text
    data = await state.get_data()
    await state.clear()
    task_id = data["current_data"]["_id"]
    new_deadline_date = data['current_data']['deadline_date']

    cur_data = dict()
    cur_data["current_data"] = await db.get_task(task_id)

    text = cur_data["current_data"]["text"]
    deadline_date = new_deadline_date
    deadline_time = new_deadline_time
    is_completed = "Да" if cur_data["current_data"]["is_completed"] else "Нет"
    created_at = cur_data["current_data"]["created_at"].strftime("%Y-%m-%d %H:%M")
    updated_at = datetime.now().strftime("%Y-%m-%d %H:%M")

    message_text = (
        f"Задача: {text}\n\n"
        f"Дедлайн: {deadline_date} {deadline_time}\n"
        f"Выполнено: {is_completed}\n"
        f"Создана: {created_at}\n"
        f"Обновлена: {updated_at}"
    )

    try:
        await db.update_task_details(task_id=task_id,
                                     new_deadline_date=deadline_date,
                                     new_deadline_time=deadline_time)
    except Exception as e:
        await message.answer("Произошла ошибка с сохранением данных")
    finally:
        await message.answer(message_text, reply_markup=task_manager_keyboard())
        new_data = dict()
        new_data["current_data"] = await db.get_task(task_id)
        await state.set_state(UserState.TASK_MANAGEMENT)
        await state.set_data(new_data)
