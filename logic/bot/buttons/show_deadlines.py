from datetime import datetime, timedelta, timezone
from itertools import groupby
from operator import itemgetter

from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext

from logic.bot.keyboards.user_keyboards import (back_keyboard,
                                                task_manager_keyboard)
from logic.bot.states.UserStates import UserState
from logic.bot.utils.decorators import clear_last_keyboard
from logic.db.database import db

router = Router()


def get_hours_left(deadline_date: str, deadline_time: str) -> int:
    """Возвращает количество часов, оставшихся до дедлайна."""
    now = datetime.now() + timedelta(hours=3)
    deadline_str = f"{deadline_date} {deadline_time}"
    deadline_dt = datetime.strptime(deadline_str, "%d.%m.%Y %H:%M")
    time_left = deadline_dt - now
    return max(0, round(time_left.total_seconds() / 3600))  # Минимум 0, чтобы не было отрицательных значений


@router.callback_query(F.data == "show_deadlines")
@clear_last_keyboard
async def show_deadline_button(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.edit_text(
        "📋 <b>Просмотр всех задач</b>\n\n"
        "✏️ Если хотите изменить задачу, просто напишите её номер.\n"
        "❗ Для возврата в главное меню используйте кнопку «Назад»."
    )

    await state.set_state(UserState.TASK_PICK)

    user_id = callback_query.from_user.id
    data = await db.get_tasks(user_id)

    if not data:
        new_message = await callback_query.message.answer("У вас нет задач", reply_markup=back_keyboard())
        # await state.clear()
        await state.set_state(UserState.MAIN_MENU)
        return new_message

    task_counter = 1
    for date, group in groupby(data, key=itemgetter("deadline_date")):
        tasks = sorted(group, key=itemgetter("deadline_time"))
        message_text = f"🗓 <b>{date}</b>\n"

        for i, task in enumerate(tasks):
            hours_left = get_hours_left(task["deadline_date"], task["deadline_time"])
            task_text = f"<b>№{task_counter + i} {task['deadline_time']}</b> ({hours_left} ч)\n"
            task_text += f"{'<s>' + task['text'] + '</s>' if task['is_completed'] else task['text']}"
            message_text += task_text + "\n"
        await callback_query.message.answer(message_text)
        task_counter += len(tasks)

    new_message = await callback_query.message.answer(
        "Вернуться назад",
        reply_markup=back_keyboard()
    )
    await state.update_data(tasks=data)
    return new_message


@router.message(F.text, UserState.TASK_PICK)
@clear_last_keyboard
async def show_details(message: types.Message, state: FSMContext):
    data = await state.get_data()

    tasks = data.get("tasks")
    tasks = sorted(tasks, key=lambda x: (x['deadline_date'], x['deadline_time']))
    if not tasks:
        new_message = await message.answer("Ошибка: задачи не найдены", reply_markup=back_keyboard())
        return new_message

    try:
        task_number = int(message.text)
        if task_number < 1 or task_number > len(tasks):
            new_message = await message.answer("Неверный номер задачи", reply_markup=back_keyboard())
            return new_message

        task = tasks[task_number - 1]

        data["current_data"] = task

        deadline_date = task["deadline_date"]
        deadline_time = task["deadline_time"]
        is_completed = "Да" if task["is_completed"] else "Нет"
        created_at = task["created_at"].strftime("%d.%m.%Y %H:%M")
        updated_at = task["updated_at"].strftime("%d.%m.%Y %H:%M")
        text = task["text"]

        reminder_date = task["reminder_date"]
        reminder_time = task["reminder_time"]
        if reminder_date and reminder_time:
            reminder_text = f"{reminder_date} {reminder_time}"
        else:
            reminder_text = "Не установлено"

        message_text = (
            f"Задача: {text}\n"
            f"Дедлайн: {deadline_date} {deadline_time}\n"
            f"Напоминание: {reminder_text}\n"
            f"Выполнено: {is_completed}\n"
            f"Создана: {created_at}\n"
            f"Обновлена: {updated_at}"
        )
        await state.set_state(UserState.TASK_MANAGEMENT)
        await state.set_data(data)
        new_message = await message.answer(message_text, reply_markup=task_manager_keyboard())

    except ValueError:
        new_message = await message.answer("Пожалуйста, введите корректный номер задачи", reply_markup=back_keyboard())
        # await state.clear()
    return new_message
