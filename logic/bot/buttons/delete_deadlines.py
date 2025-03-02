from aiogram import F, Router, types
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext

from logic.bot.keyboards.user_keyboards import back_keyboard
from logic.bot.states.UserStates import UserState
from logic.db.database import db

router = Router()


@router.callback_query(F.data == "delete_deadlines")
async def delete_deadlines_button(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.edit_text("Вы выбрали 'Удаление записей'\n\n"
                                           "Введите дату, с которой нужно удалить все дедлайны",
                                           reply_markup=back_keyboard())
    await state.set_state(UserState.TASK_DELETE_ON_DATE)


@router.message(F.text, UserState.TASK_DELETE_ON_DATE)
async def delete_deadlines(message: types.Message, state: FSMContext):
    date = message.text
    user_id = message.from_user.id
    try:
        await db.delete_tasks_by_date(user_id=user_id, date=date)
        await message.answer(f"Задачи на <i>{date}</i> были успешно удалены",
                             parse_mode=ParseMode.HTML, reply_markup=back_keyboard())
    except Exception as e:
        await message.answer(f"Произошла ошибка при удалении", reply_markup=back_keyboard())
    finally:
        await state.clear()
