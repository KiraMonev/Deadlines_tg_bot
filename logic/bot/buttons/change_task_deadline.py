from datetime import datetime

from aiogram import F, Router, types
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext

from logic.bot.keyboards.user_keyboards import (back_keyboard, remove_keyboard,
                                                task_manager_keyboard)
from logic.bot.states.UserStates import UserState
from logic.bot.utils.parser import parse_date, parse_time
from logic.db.database import db

router = Router()


@router.callback_query(F.data == "change_deadline")
async def change_deadline_button(callback_query: types.CallbackQuery, state: FSMContext):
    await state.set_state(UserState.TASK_CHANGE_DATE)
    message = await callback_query.message.edit_text(
        "🗓 Назначьте новую <b>дату</b> этой задаче",
        reply_markup=back_keyboard(),
        parse_mode=ParseMode.HTML
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
            parse_mode=ParseMode.HTML,
            reply_markup=back_keyboard()
        )
        await state.update_data(last_message_id=new_message.message_id)
        return

    await state.update_data(deadline_date=new_date)
    await state.set_state(UserState.TASK_CHANGE_TIME)
    new_message = await message.answer(f"🗓 Новая дата: <i>{new_date}</i>\n\n"
                                       "⏰ Введите новое <b>время</b> для дедлайна",
                                       parse_mode=ParseMode.HTML,
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
            parse_mode=ParseMode.HTML,
            reply_markup=back_keyboard()
        )
        await state.update_data(last_message_id=new_message.message_id)
        return

    task_id = data.get("current_data", {}).get("_id")
    new_date = data.get("deadline_date")

    if not task_id:
        new_message = await message.answer("Ошибка: не найдена текущая задача.",
                                           reply_markup=back_keyboard()
                                           )
        await state.update_data(last_message_id=new_message.message_id)
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
