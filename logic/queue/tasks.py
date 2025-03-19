import asyncio
import logging
from datetime import datetime, timedelta, timezone

from celery import shared_task

from logic.bot import bot
from logic.db.database import db


@shared_task
def check_reminders():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(check_reminders_async())


async def send_reminder(task):
    user_id = task["user_id"]
    deadline_date = task["deadline_date"]
    deadline_time = task["deadline_time"]
    try:
        await bot.send_message(
            chat_id=user_id,
            text=f"Задача с дедлайном <i>{deadline_date} {deadline_time}</i> будет просрочена совсем скоро!"
        )
        print(f"Напоминание отправлено пользователю {user_id} о задаче {task['_id']}")
    except Exception as e:
        print(f"Не удалось отправить напоминание пользователю {user_id}: {e}")


async def check_reminders_async():
    try:
        tasks = await db.get_tasks_with_reminders_date_and_time()
        print(f"Получено задач для напоминания: {len(tasks)}, "
              f"Время: {datetime.now(timezone.utc) + timedelta(hours=3)}")
        if tasks:
            await asyncio.gather(*[send_reminder(task) for task in tasks])
    except Exception as e:
        print(f"Общая ошибка при отправке напоминаний: {e}")


@shared_task
def prolonging_tasks():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(prolonging_tasks_async())


async def prolong_task(task):
    user_id = task["user_id"]
    deadline_date = task["deadline_date"]
    deadline_time = task["deadline_time"]
    try:
        now = datetime.now(timezone.utc)
        new_date = (now + timedelta(days=1, hours=3)).strftime("%d.%m.%Y")
        await db.update_task_details(task_id=task["_id"], new_deadline_date=new_date)
        try:
            await bot.send_message(
                chat_id=user_id,
                text=f"Задача с дедлайном <i>{deadline_date} {deadline_time}</i> продлена на 1 день!"
            )
            print(f"Напоминание отправлено пользователю {user_id} о задаче {task['_id']}")
        except Exception as e:
            logging.error(f"Не удалось отправить напоминание пользователю {user_id}: {e}")
    except Exception as e:
        logging.error(f"Не удалось продлить задачу пользователю {user_id}: {e}")


async def prolonging_tasks_async():
    try:
        tasks = await db.get_overdue_tasks()
        print(f"Получено задач для продления: {len(tasks)}, "
              f"Время: {datetime.now(timezone.utc) + timedelta(hours=3)}")
        if tasks:
            await asyncio.gather(*[prolong_task(task) for task in tasks])

    except Exception as e:
        logging.error(f"Общая ошибка при отправке напоминаний: {e}")
