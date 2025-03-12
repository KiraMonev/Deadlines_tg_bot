import logging
from datetime import datetime, timedelta

from aiogram import F, Router, types
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from logic.bot.keyboards.user_keyboards import (back_keyboard,
                                                reminder_time_keyboard,
                                                remove_keyboard)
from logic.bot.states.UserStates import UserState
from logic.bot.utils.parser import calculate_reminder, parse_date, parse_time
from logic.db.database import db

router = Router()


@router.callback_query(F.data == "new_deadline")
async def new_deadline_button(callback_query: types.CallbackQuery, state: FSMContext):
    await state.set_state(UserState.TASK_ADD_TEXT)
    message = await callback_query.message.edit_text(
        "📝 <b>Добавление новой задачи</b>\n\n"
        "✏️ Введите <b>текст</b> задачи, которую собираетесь выполнить.",
        reply_markup=back_keyboard(),
        parse_mode=ParseMode.HTML
    )
    await state.update_data(last_message_id=message.message_id)


@router.message(F.text, UserState.TASK_ADD_TEXT)
async def set_deadline_text(message: Message, state: FSMContext):
    data = await state.get_data()
    last_message_id = data.get("last_message_id")
    if last_message_id:
        await remove_keyboard(message.bot, message.chat.id, last_message_id)

    await state.update_data(data_text=message.text)
    await state.set_state(UserState.TASK_ADD_DATE)
    new_message = await message.answer(
        "✍️ <b>Отлично!</b> Теперь давайте назначим дату.\n\n"
        "🗓 Напишите <b>дату</b> для планируемого дедлайна.",
        parse_mode=ParseMode.HTML,
        reply_markup=back_keyboard()
    )
    await state.update_data(last_message_id=new_message.message_id)


@router.message(F.text, UserState.TASK_ADD_DATE)
async def set_deadline_date(message: Message, state: FSMContext):
    data = await state.get_data()
    last_message_id = data.get("last_message_id")
    if last_message_id:
        await remove_keyboard(message.bot, message.chat.id, last_message_id)

    formatted_date = parse_date(message.text)
    if not formatted_date:
        new_message = await message.answer(
            "<b>Неверный формат даты</b>\n\n"
            "Пожалуйста, введите дату в одном из следующих форматов:\n"
            "<code>ДД.ММ</code> или <code>ДД.ММ.ГГГГ</code>.",
            parse_mode=ParseMode.HTML,
            reply_markup=back_keyboard()
        )
        await state.update_data(last_message_id=new_message.message_id)
        return

    await state.update_data(data_date=formatted_date)
    data = await state.get_data()
    await state.set_state(UserState.TASK_ADD_TIME)
    new_message = await message.answer(
        f"🗓 Получили дату: <i>{data['data_date']}</i>\n\n"
        "⏰ Теперь введите <b>время</b> для дедлайна.",
        parse_mode=ParseMode.HTML,
        reply_markup=back_keyboard()
    )
    await state.update_data(last_message_id=new_message.message_id)


@router.message(F.text, UserState.TASK_ADD_TIME)
async def set_deadline_time(message: Message, state: FSMContext):
    data = await state.get_data()
    last_message_id = data.get("last_message_id")
    if last_message_id:
        await remove_keyboard(message.bot, message.chat.id, last_message_id)

    formatted_time = parse_time(message.text)
    if not formatted_time:
        new_message = await message.answer(
            "<b>Неверный формат времени</b>\n\n"
            "Пожалуйста, введите время в формате <code>ЧЧ:ММ</code>.",
            parse_mode=ParseMode.HTML,
            reply_markup=back_keyboard()
        )
        await state.update_data(last_message_id=new_message.message_id)
        return

    await state.update_data(data_time=formatted_time)
    new_message = await message.answer(
        f"🗓 Получили время: <i>{data['data_date']}</i>\n\n"
        "⏰ Теперь установите <b>напоминание</b> для дедлайна.",
        parse_mode=ParseMode.HTML,
        reply_markup=reminder_time_keyboard()
    )
    await state.update_data(last_message_id=new_message.message_id)
    await state.set_state(UserState.TASK_ADD_REMINDER_TIME)


REMINDER_TIMES = {
    "reminder_1h": timedelta(hours=1),
    "reminder_4h": timedelta(hours=4),
    "reminder_1d": timedelta(days=1),
    "reminder_none": None,  # Отсутствие напоминания
}


@router.callback_query(F.data.in_(REMINDER_TIMES.keys()), UserState.TASK_ADD_REMINDER_TIME)
async def set_reminder_time(callback_query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    last_message_id = data.get("last_message_id")
    if last_message_id:
        await remove_keyboard(callback_query.bot, callback_query.message.chat.id, last_message_id)

    reminder_offset = REMINDER_TIMES[callback_query.data]
    reminder_date, reminder_time = await calculate_reminder(reminder_offset=reminder_offset, data=data)

    try:
        await db.add_task(user_id=callback_query.from_user.id,
                          text=data["data_text"],
                          deadline_date=data["data_date"],
                          deadline_time=data["data_time"],
                          reminder_date=reminder_date,
                          reminder_time=reminder_time)
        await callback_query.message.edit_text(
            f"✅ <b>Задача сохранена!</b>\n\n"
            f"Задача: {data['data_text']}\n"
            f"Дедлайн: <i>{data['data_date']} {data['data_time']}</i>\n\n"
            "Все в целости и сохранности! 👍",
            reply_markup=back_keyboard(),
            parse_mode=ParseMode.HTML
        )

    except Exception as e:
        logging.error(e)
        await callback_query.answer(f"Произошла некоторая ошибка, попробуйте ещё раз позже",
                                    reply_markup=back_keyboard())
    finally:
        await state.clear()
