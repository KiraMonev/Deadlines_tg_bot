from datetime import datetime

from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext

from logic.bot.keyboards.user_keyboards import (back_keyboard,
                                                task_manager_keyboard)
from logic.bot.states.UserStates import UserState
from logic.bot.utils.parser import parse_date, parse_time
from logic.db.database import db

router = Router()


@router.callback_query(F.data == "change_deadline")
async def change_deadline_button(callback_query: types.CallbackQuery, state: FSMContext):
    await state.set_state(UserState.TASK_CHANGE_DATE)
    await callback_query.message.edit_text("Назначьте новую дату этой задаче", reply_markup=back_keyboard())


@router.message(F.text, UserState.TASK_CHANGE_DATE)
async def exchange_deadline_date(message: types.Message, state: FSMContext):
    new_date = parse_date(message.text)
    if not new_date:
        await message.answer("Неверный формат даты. Введите дату в формате ДД.ММ или ДД.ММ.ГГГГ")
        return

    await state.update_data(deadline_date=new_date)
    await state.set_state(UserState.TASK_CHANGE_TIME)
    await message.answer(f"Новая дата: {new_date}\nВведите новое время для дедлайна")


@router.message(F.text, UserState.TASK_CHANGE_TIME)
async def exchange_deadline_time(message: types.Message, state: FSMContext):
    new_time = parse_time(message.text)
    if not new_time:
        await message.answer("Неверный формат времени. Введите время в формате ЧЧ:ММ")
        return

    data = await state.get_data()
    task_id = data.get("current_data", {}).get("_id")
    new_date = data.get("deadline_date")

    if not task_id:
        await message.answer("Ошибка: не найдена текущая задача.")
        return

    try:
        await db.update_task_details(task_id=task_id, new_deadline_date=new_date, new_deadline_time=new_time)
        task = await db.get_task(task_id)

        message_text = (
            f"Задача: {task['text']}\n\n"
            f"Дедлайн: {new_date} {new_time}\n"
            f"Выполнено: {'Да' if task['is_completed'] else 'Нет'}\n"
            f"Создана: {task['created_at'].strftime('%Y-%m-%d %H:%M')}\n"
            f"Обновлена: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        )
        await message.answer(message_text, reply_markup=task_manager_keyboard())

    except Exception as e:
        await message.answer("Произошла ошибка при обновлении дедлайна.")

    finally:
        await state.set_state(UserState.TASK_MANAGEMENT)
        await state.update_data(current_data=await db.get_task(task_id))
