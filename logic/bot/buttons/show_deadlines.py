from itertools import groupby
from operator import itemgetter

from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext

from logic.bot.keyboards.user_keyboards import task_manager_keyboard
from logic.bot.states.UserStates import UserState
from logic.db.database import db

router = Router()


@router.callback_query(F.data == "show_deadlines")
async def show_deadline_button(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.edit_text(
        "Вы выбрали 'Просмотр всех записей'\n\n"
        "Напишите номер задачи, которую хотите просмотреть"
    )
    await state.set_state(UserState.TASK_PICK)

    user_id = callback_query.from_user.id
    data = await db.get_tasks(user_id)

    if not data:
        await callback_query.message.answer("У вас нет задач")
        await state.clear()
        return

    sorted_data = sorted(data, key=lambda x: (x["deadline_date"], x["created_at"]))

    task_counter = 1
    for date, group in groupby(sorted_data, key=itemgetter("deadline_date")):
        tasks = list(group)
        message_text = f"{date}\n" + "\n".join(
            f"{task_counter + i}. {task['text']}" for i, task in enumerate(tasks)
        )
        await callback_query.message.answer(message_text)
        task_counter += len(tasks)

    await state.update_data(tasks=sorted_data)


@router.message(F.text, UserState.TASK_PICK)
async def show_details(message: types.Message, state: FSMContext):
    data = await state.get_data()
    tasks = data.get("tasks")
    if not tasks:
        await message.answer("Ошибка: задачи не найдены")
        return

    try:
        task_number = int(message.text)
        if task_number < 1 or task_number > len(tasks):
            await message.answer("Неверный номер задачи")
            return

        task = tasks[task_number - 1]

        data["current_data"] = task

        deadline_date = task["deadline_date"]
        deadline_time = task["deadline_time"]
        is_completed = "Да" if task["is_completed"] else "Нет"
        # reminder_date = task["reminder_date"]
        # reminder_time = task["reminder_time"]
        created_at = task["created_at"].strftime("%Y-%m-%d %H:%M")
        updated_at = task["updated_at"].strftime("%Y-%m-%d %H:%M")
        text = task["text"]

        message_text = (
            f"Задача: {text}\n\n"
            f"Дедлайн: {deadline_date} {deadline_time}\n"
            f"Выполнено: {is_completed}\n"
            f"Создана: {created_at}\n"
            f"Обновлена: {updated_at}"
        )
        await state.set_state(UserState.TASK_MANAGEMENT)
        await state.set_data(data)
        await message.answer(message_text, reply_markup=task_manager_keyboard())

    except ValueError:
        await message.answer("Пожалуйста, введите корректный номер задачи")
        await state.clear()
