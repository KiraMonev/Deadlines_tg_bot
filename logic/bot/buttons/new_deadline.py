import logging
from datetime import timedelta

from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from logic.bot.keyboards.user_keyboards import (back_keyboard,
                                                reminder_time_keyboard)
from logic.bot.states.UserStates import UserState
from logic.bot.utils.decorators import clear_last_keyboard
from logic.bot.utils.parser import calculate_reminder, parse_date, parse_time
from logic.db.database import db

router = Router()


@router.callback_query(F.data == "new_deadline")
@clear_last_keyboard
async def new_deadline_button(callback_query: types.CallbackQuery, state: FSMContext):
    await state.set_state(UserState.TASK_ADD_TEXT)
    message = await callback_query.message.edit_text(
        "📝 <b>Добавление новой задачи</b>\n\n"
        "✏️ Введите <b>текст</b> задачи, которую собираетесь выполнить.",
        reply_markup=back_keyboard()
    )
    return message


@router.message(F.text, UserState.TASK_ADD_TEXT)
@clear_last_keyboard
async def set_deadline_text(message: Message, state: FSMContext):
    await state.update_data(data_text=message.text)
    await state.set_state(UserState.TASK_ADD_DATE)
    new_message = await message.answer(
        "✍️ <b>Отлично!</b> Теперь давайте назначим дату.\n\n"
        "🗓 Напишите <b>дату</b> для планируемого дедлайна.",
        reply_markup=back_keyboard()
    )
    return new_message


@router.message(F.text, UserState.TASK_ADD_DATE)
@clear_last_keyboard
async def set_deadline_date(message: Message, state: FSMContext):
    formatted_date = parse_date(message.text)
    if not formatted_date:
        new_message = await message.answer(
            "<b>Неверный формат даты</b>\n\n"
            "Пожалуйста, введите дату в одном из следующих форматов:\n"
            "<code>ДД.ММ</code> или <code>ДД.ММ.ГГГГ</code>.",
            reply_markup=back_keyboard()
        )
        return new_message

    await state.update_data(data_date=formatted_date)
    data = await state.get_data()
    await state.set_state(UserState.TASK_ADD_TIME)
    new_message = await message.answer(
        f"🗓 Получили дату: <i>{data['data_date']}</i>\n\n"
        "⏰ Теперь введите <b>время</b> для дедлайна.",
        reply_markup=back_keyboard()
    )
    return new_message


@router.message(F.text, UserState.TASK_ADD_TIME)
@clear_last_keyboard
async def set_deadline_time(message: Message, state: FSMContext):
    formatted_time = parse_time(message.text)
    if not formatted_time:
        new_message = await message.answer(
            "<b>Неверный формат времени</b>\n\n"
            "Пожалуйста, введите время в формате <code>ЧЧ:ММ</code>.",
            reply_markup=back_keyboard()
        )
        return new_message

    await state.update_data(data_time=formatted_time)
    data = await state.get_data()
    new_message = await message.answer(
        f"🗓 Получили время: <i>{data['data_time']}</i>\n\n"
        "⏰ Теперь установите <b>напоминание</b> для дедлайна.",
        reply_markup=reminder_time_keyboard()
    )
    await state.set_state(UserState.TASK_ADD_REMINDER_TIME)
    return new_message


REMINDER_TIMES = {
    "reminder_1h": timedelta(hours=1),
    "reminder_4h": timedelta(hours=4),
    "reminder_1d": timedelta(days=1),
    "reminder_none": None,  # Отсутствие напоминания
}


@router.callback_query(F.data.in_(REMINDER_TIMES.keys()), UserState.TASK_ADD_REMINDER_TIME)
@clear_last_keyboard
async def set_reminder_time(callback_query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()

    reminder_offset = REMINDER_TIMES[callback_query.data]
    reminder_date, reminder_time = await calculate_reminder(
        reminder_offset=reminder_offset,
        date=data["data_date"],
        time=data["data_time"]
    )

    try:
        await db.add_task(user_id=callback_query.from_user.id,
                          text=data["data_text"],
                          deadline_date=data["data_date"],
                          deadline_time=data["data_time"],
                          reminder_date=reminder_date,
                          reminder_time=reminder_time)
        new_message = await callback_query.message.edit_text(
            f"✅ <b>Задача сохранена!</b>\n\n"
            f"Задача: {data['data_text']}\n"
            f"Дедлайн: <i>{data['data_date']} {data['data_time']}</i>\n\n"
            "Все в целости и сохранности! 👍",
            reply_markup=back_keyboard(),
        )

    except Exception as e:
        logging.error(e)
        new_message = await callback_query.answer(f"Произошла некоторая ошибка, попробуйте ещё раз позже",
                                                  reply_markup=back_keyboard())
    finally:
        await state.set_state(UserState.MAIN_MENU)
    return new_message
