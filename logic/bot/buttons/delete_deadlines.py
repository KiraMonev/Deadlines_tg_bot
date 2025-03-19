from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext

from logic.bot.keyboards.user_keyboards import back_keyboard
from logic.bot.states.UserStates import UserState
from logic.bot.utils.decorators import clear_last_keyboard
from logic.bot.utils.parser import parse_date
from logic.db.database import db

router = Router()


@router.callback_query(F.data == "delete_deadlines")
@clear_last_keyboard
async def delete_deadlines_button(callback_query: types.CallbackQuery, state: FSMContext):
    message = await callback_query.message.edit_text(
        "🗑 <b>Удаление записей</b>\n\n"
        "🗓 Введите <b>дату</b>, с которой нужно удалить все дедлайны.",
        reply_markup=back_keyboard(),
    )
    await state.set_state(UserState.TASK_DELETE_ON_DATE)
    return message


@router.message(F.text, UserState.TASK_DELETE_ON_DATE)
@clear_last_keyboard
async def delete_deadlines(message: types.Message, state: FSMContext):
    date = parse_date(message.text)
    if not date:
        new_message = await message.answer(
            "<b>Неверный формат даты</b>\n\n"
            "Пожалуйста, введите дату в формате <code>ДД.ММ</code> или <code>ДД.ММ.ГГГГ</code>.",
            reply_markup=back_keyboard()
        )
        return new_message

    # Логика удаления дедлайнов
    user_id = message.from_user.id
    tasks = await db.collection.find({"user_id": user_id, "deadline_date": date}).to_list(length=None)
    if not tasks:
        new_message = await message.answer(
            f"<b>Нет задач на {date}</b>",
            reply_markup=back_keyboard()
        )
        return new_message

    await db.delete_tasks_by_date(user_id=user_id, date=date)
    new_message = await message.answer(
        f"Задачи на <i>{date}</i> успешно удалены",
        reply_markup=back_keyboard()
    )
    return new_message
    # await state.clear()
