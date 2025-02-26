import datetime
from collections import defaultdict

from aiogram import F, Router, types

from logic.bot.keyboards.user_keyboards import back_keyboard
from logic.db.database import db

router = Router()


@router.callback_query(F.data == "show_deadlines")
async def show_deadline_button(callback_query: types.CallbackQuery):
    await callback_query.message.edit_text("Вы выбрали 'Просмотр всех записей'",
                                           reply_markup=back_keyboard())

    user_id = callback_query.from_user.id
    data = await db.get_tasks(user_id)
    tasks_by_date = defaultdict(list)
    for task in data:
        deadline_text = str(task["text"])
        deadline_date = task["deadline_date"]
        deadline_time = task["deadline_time"]
        is_completed = bool(task["is_completed"])
        reminder_date = task["reminder_date"]
        reminder_time = task["reminder_time"]
        created_at = datetime.datetime.strftime(task["created_at"], "%Y-%m-%d %H:%M")
        updated_at = datetime.datetime.strftime(task["updated_at"], "%Y-%m-%d %H:%M")
        tasks_by_date[deadline_date].append(deadline_text)

    task_counter = 1
    for date, tasks in sorted(tasks_by_date.items()):
        message_text = f"{date}\n" + "\n".join(f"{task_counter + i}. {task}" for i, task in enumerate(tasks))
        task_counter += len(tasks)
        await callback_query.message.answer(message_text)
