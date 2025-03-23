import asyncio
import logging
from datetime import datetime, timedelta

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
    text = task["text"]
    try:
        await bot.send_message(
            chat_id=user_id,
            text=(
                "📌 <b>Напоминание о задаче!</b>\n"
                f"Задача: {text}\n"
                f"Дедлайн: <i>{deadline_date} {deadline_time}</i>\n"
                "Она скоро будет просрочена! Постарайтесь выполнить её вовремя."
            ))
    except Exception as e:
        logging.error(f"Не удалось отправить напоминание пользователю {user_id}: {e}")


async def check_reminders_async():
    try:
        tasks = await db.get_tasks_with_reminders_date_and_time()
        if tasks:
            await asyncio.gather(*[send_reminder(task) for task in tasks])
    except Exception as e:
        logging.error(f"Общая ошибка при отправке напоминаний: {e}")


@shared_task
def prolonging_tasks():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(prolonging_tasks_async())


async def prolong_task(task):
    user_id = task["user_id"]
    deadline_date = task["deadline_date"]
    deadline_time = task["deadline_time"]
    reminder_date = task["reminder_date"]
    text = task["text"]
    try:

        new_deadline = datetime.strptime(deadline_date, "%d.%m.%Y") + timedelta(days=1)
        new_deadline_str = new_deadline.strftime("%d.%m.%Y")

        new_reminder = datetime.strptime(reminder_date, "%d.%m.%Y") + timedelta(days=1)
        new_reminder_str = new_reminder.strftime("%d.%m.%Y")

        await db.update_task_details(
            task_id=task["_id"],
            new_deadline_date=new_deadline_str,
            reminder_date=new_reminder_str
        )
        try:
            await bot.send_message(
                chat_id=user_id,
                text=(
                    "📌 <b>Ваша задача продлена!</b>\n"
                    f"Задача: <i>{text}</i>\n\n"
                    f"Старый дедлайн: <i>{deadline_date} {deadline_time}</i>\n"
                    f"Новый дедлайн: <i>{new_deadline_str} {deadline_time}</i>\n\n"
                    "У вас есть ещё 1 день, чтобы завершить задачу!"
                ))
        except Exception as e:
            logging.error(f"Не удалось отправить напоминание пользователю {user_id}: {e}")
    except Exception as e:
        logging.error(f"Не удалось продлить задачу пользователю {user_id}: {e}")


async def prolonging_tasks_async():
    try:
        tasks = await db.get_overdue_tasks()
        if tasks:
            await asyncio.gather(*[prolong_task(task) for task in tasks])

    except Exception as e:
        logging.error(f"Общая ошибка при отправке напоминаний: {e}")
