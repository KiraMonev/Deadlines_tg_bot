import logging

from aiogram import F, Router, types
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from logic.bot.keyboards.user_keyboards import back_keyboard
from logic.bot.states.UserStates import UserState
from logic.bot.utils.parser import parse_date, parse_time
from logic.db.database import db

router = Router()


@router.callback_query(F.data == "new_deadline")
async def new_deadline_button(callback_query: types.CallbackQuery, state: FSMContext):
    await state.set_state(UserState.TASK_ADD_TEXT)
    await callback_query.message.edit_text(
        "📝 <b>Добавление новой задачи</b>\n\n"
        "✏️ Введите текст задачи, которую собираетесь выполнить.",
        reply_markup=back_keyboard(),
        parse_mode=ParseMode.HTML
    )


@router.message(F.text, UserState.TASK_ADD_TEXT)
async def set_deadline_text(message: Message, state: FSMContext):
    await state.update_data(data_text=message.text)
    await state.set_state(UserState.TASK_ADD_DATE)
    await message.answer(
        "✍️ <b>Отлично!</b> Теперь давайте назначим дату.\n\n"
        "📅 Напишите <b>дату</b> для планируемого дедлайна.",
        parse_mode=ParseMode.HTML
    )

@router.message(F.text, UserState.TASK_ADD_DATE)
async def set_deadline_date(message: Message, state: FSMContext):
    formatted_date = parse_date(message.text)
    if not formatted_date:
        await message.answer(
            "<b>Неверный формат даты</b>\n\n"
            "Пожалуйста, введите дату в одном из следующих форматов:\n"
            "<code>ДД.ММ</code> или <code>ДД.ММ.ГГГГ</code>.",
            parse_mode=ParseMode.HTML
        )
        return

    await state.update_data(data_date=formatted_date)
    data = await state.get_data()
    await state.set_state(UserState.TASK_ADD_TIME)
    await message.answer(
        f"⏰ Получили дату: <i>{data['data_date']}</i>\n\n"
        "⏳ Теперь введите <b>время</b> для дедлайна.",
        parse_mode=ParseMode.HTML
    )


@router.message(F.text, UserState.TASK_ADD_TIME)
async def set_deadline_time(message: Message, state: FSMContext):
    formatted_time = parse_time(message.text)
    if not formatted_time:
        await message.answer(
            "<b>Неверный формат времени</b>\n\n"
            "Пожалуйста, введите время в формате <code>ЧЧ:ММ</code>.",
            parse_mode=ParseMode.HTML
        )

        return

    await state.update_data(data_time=formatted_time)
    data = await state.get_data()
    try:
        await db.add_task(user_id=message.from_user.id,
                          text=data["data_text"],
                          deadline_date=data["data_date"],
                          deadline_time=data["data_time"],
                          reminder_date="pass",
                          reminder_time="pass")
        # добавить подтверждение добавления задачи
        await message.answer(
            f"✅ <b>Задача сохранена!</b>\n\n"
            f"Задача: <b>{data['data_text']}</b>\n"
            f"Дедлайн: <i>{data['data_date']} {data['data_time']}</i>\n\n"
            "Все в целости и сохранности! 👍",
            reply_markup=back_keyboard(),
            parse_mode=ParseMode.HTML
        )

    except Exception as e:
        logging.error(e)
        await message.answer(f"Произошла некоторая ошибка, попробуйте ещё раз позже",
                             reply_markup=back_keyboard())
    finally:
        await state.clear()
