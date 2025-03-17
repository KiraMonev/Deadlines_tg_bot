import logging
from datetime import datetime

from aiogram import F, Router, types
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext

from logic.bot.keyboards.user_keyboards import (back_keyboard, remove_keyboard,
                                                task_manager_keyboard)
from logic.bot.states.UserStates import UserState
from logic.db.database import db

router = Router()


@router.callback_query(F.data == "change_text")
async def change_text_button(callback_query: types.CallbackQuery, state: FSMContext):
    await state.set_state(UserState.TASK_CHANGE_TEXT)
    message = await callback_query.message.edit_text(
        "✏️ Назначьте новый <b>текст</b> этой задаче",
        reply_markup=back_keyboard(),
    )
    await state.update_data(last_message_id=message.message_id)


@router.message(F.text, UserState.TASK_CHANGE_TEXT)
async def exchange_text(message: types.Message, state: FSMContext):
    data = await state.get_data()
    last_message_id = data.get("last_message_id")
    if last_message_id:
        await remove_keyboard(message.bot, message.chat.id, last_message_id)

    new_text = message.text
    await state.clear()
    task_id = data["current_data"]["_id"]

    cur_data = dict()
    cur_data["current_data"] = await db.get_task(task_id)

    deadline_date = cur_data["current_data"]["deadline_date"]
    deadline_time = cur_data["current_data"]["deadline_time"]
    is_completed = "Да" if cur_data["current_data"]["is_completed"] else "Нет"
    created_at = cur_data["current_data"]["created_at"].strftime("%Y-%m-%d %H:%M")
    updated_at = datetime.now().strftime("%Y-%m-%d %H:%M")

    reminder_date = cur_data["current_data"]["reminder_date"]
    reminder_time = cur_data["current_data"]["reminder_time"]
    if reminder_date and reminder_time:
        reminder_text = f"{reminder_date} {reminder_time}"
    else:
        reminder_text = "Не установлено"

    message_text = (
        f"✅ <b>Задача обновлена!</b>\n\n"
        f"Задача: {new_text}\n"
        f"Дедлайн: {deadline_date} {deadline_time}\n"
        f"Напоминание: {reminder_text}\n"
        f"Выполнено: {is_completed}\n"
        f"Создана: {created_at}\n"
        f"Обновлена: {updated_at}"
    )

    try:
        await db.update_task_details(task_id=task_id, new_text=new_text)
    except Exception as e:
        logging.error(e)
        await message.answer(
            "Произошла ошибка с сохранением нового текста",
            reply_markup=back_keyboard()
        )
    finally:
        await message.answer(message_text, reply_markup=task_manager_keyboard(), parse_mode=ParseMode.HTML)
        new_data = dict()
        new_data["current_data"] = await db.get_task(task_id)
        await state.set_state(UserState.TASK_MANAGEMENT)
        await state.set_data(new_data)
