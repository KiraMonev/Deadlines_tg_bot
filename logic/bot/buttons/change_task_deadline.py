import logging
from datetime import datetime, timedelta

from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext

from logic.bot.keyboards.user_keyboards import (back_keyboard,
                                                reminder_time_keyboard,
                                                remove_keyboard,
                                                task_manager_keyboard)
from logic.bot.states.UserStates import UserState
from logic.bot.utils.parser import calculate_reminder, parse_date, parse_time
from logic.db.database import db

router = Router()


@router.callback_query(F.data == "change_deadline")
async def change_deadline_button(callback_query: types.CallbackQuery, state: FSMContext):
    await state.set_state(UserState.TASK_CHANGE_DATE)
    message = await callback_query.message.edit_text(
        "🗓 Назначьте новую <b>дату</b> этой задаче",
        reply_markup=back_keyboard(),
    )
    await state.update_data(last_message_id=message.message_id)


@router.message(F.text, UserState.TASK_CHANGE_DATE)
async def exchange_deadline_date(message: types.Message, state: FSMContext):
    data = await state.get_data()
    last_message_id = data.get("last_message_id")
    if last_message_id:
        await remove_keyboard(message.bot, message.chat.id, last_message_id)

    new_date = parse_date(message.text)
    if not new_date:
        new_message = await message.answer(
            "<b>Неверный формат даты</b>\n\n"
            "Пожалуйста, введите дату в одном из следующих форматов:\n"
            "<code>ДД.ММ</code> или <code>ДД.ММ.ГГГГ</code>.",
            reply_markup=back_keyboard()
        )
        await state.update_data(last_message_id=new_message.message_id)
        return

    await state.update_data(deadline_date=new_date)
    await state.set_state(UserState.TASK_CHANGE_TIME)
    new_message = await message.answer(
        f"🗓 Новая дата: <i>{new_date}</i>\n\n"
        "⏰ Введите новое <b>время</b> для дедлайна",
        reply_markup=back_keyboard()
    )
    await state.update_data(last_message_id=new_message.message_id)


@router.message(F.text, UserState.TASK_CHANGE_TIME)
async def exchange_deadline_time(message: types.Message, state: FSMContext):
    data = await state.get_data()
    last_message_id = data.get("last_message_id")
    if last_message_id:
        await remove_keyboard(message.bot, message.chat.id, last_message_id)

    new_time = parse_time(message.text)
    if not new_time:
        new_message = await message.answer(
            "<b>Неверный формат времени</b>\n\n"
            "Пожалуйста, введите время в формате <code>ЧЧ:ММ</code>.",
            reply_markup=back_keyboard()
        )
        await state.update_data(last_message_id=new_message.message_id)
        return

    task_id = data.get("current_data", {}).get("_id")
    new_date = data.get("deadline_date")

    if not task_id:
        new_message = await message.answer(
            "Ошибка: не найдена текущая задача.",
            reply_markup=back_keyboard()
        )
        await state.update_data(last_message_id=new_message.message_id)
        return

    await state.update_data(new_deadline_time=new_time)
    new_message = await message.answer(
        f"🗓 Новый дедлайн: <i>{new_date} {new_time}</i>\n\n"
        "⏰ Теперь установите <b>напоминание</b> для дедлайна.",
        reply_markup=reminder_time_keyboard()
    )
    await state.update_data(last_message_id=new_message.message_id)
    await state.set_state(UserState.TASK_CHANGE_REMINDER_TIME)


REMINDER_TIMES = {
    "reminder_1h": timedelta(hours=1),
    "reminder_4h": timedelta(hours=4),
    "reminder_1d": timedelta(days=1),
    "reminder_none": None,
}


@router.callback_query(F.data.in_(REMINDER_TIMES.keys()), UserState.TASK_CHANGE_REMINDER_TIME)
async def change_reminder_time(callback_query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    last_message_id = data.get("last_message_id")
    if last_message_id:
        await remove_keyboard(callback_query.bot, callback_query.message.chat.id, last_message_id)

    task_id = data.get("current_data", {}).get("_id")
    new_date = data.get("deadline_date")
    new_time = data.get("new_deadline_time")

    if not task_id:
        await callback_query.answer("Ошибка: не найдена текущая задача.")
        return

    reminder_offset = REMINDER_TIMES[callback_query.data]
    reminder_date, reminder_time = await calculate_reminder(
        reminder_offset=reminder_offset,
        date=data["deadline_date"],
        time=data["new_deadline_time"]
    )

    try:
        await db.update_task_details(
            task_id=task_id,
            new_deadline_date=new_date,
            new_deadline_time=new_time,
            reminder_date=reminder_date,
            reminder_time=reminder_time
        )
        task = await db.get_task(task_id)

        if reminder_date and reminder_time:
            reminder_text = f"{reminder_date} {reminder_time}"
        else:
            reminder_text = "Не установлено"

        message_text = (
            f"✅ <b>Задача обновлена!</b>\n\n"
            f"Задача: {task['text']}\n"
            f"Дедлайн: {new_date} {new_time}\n"
            f"Напоминание: {reminder_text}\n"
            f"Выполнено: {'Да' if task['is_completed'] else 'Нет'}\n"
            f"Создана: {task['created_at'].strftime('%Y-%m-%d %H:%M')}\n"
            f"Обновлена: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        )
        await callback_query.message.edit_text(
            message_text,
            reply_markup=task_manager_keyboard(),
        )
    except Exception as e:
        logging.error(e)
        await callback_query.answer("Произошла ошибка при обновлении дедлайна.")
    finally:
        await state.set_state(UserState.TASK_MANAGEMENT)
        await state.update_data(current_data=await db.get_task(task_id))
