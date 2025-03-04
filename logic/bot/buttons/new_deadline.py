import logging

from aiogram import F, Router, types
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from logic.bot.keyboards.user_keyboards import back_keyboard
from logic.bot.states.UserStates import UserState
from logic.db.database import db

router = Router()


@router.callback_query(F.data == "new_deadline")
async def new_deadline_button(callback_query: types.CallbackQuery, state: FSMContext):
    await state.set_state(UserState.TASK_ADD_TEXT)
    await callback_query.message.edit_text("Вы выбрали 'Добавление новой записи'\n\n"
                                           "Введите текст задачи, которую собираетесь выполнить",
                                           reply_markup=back_keyboard())


@router.message(F.text, UserState.TASK_ADD_TEXT)
async def set_deadline_text(message: Message, state: FSMContext):
    data = {"data_text": message.text}
    await state.set_state(UserState.TASK_ADD_DATE)
    await message.answer(f"Отличное дело! Давайте назначим ему дату и время, чтобы не забыть его сдать!\n\n"
                         f"Напишите дату планируемого дедлайна")
    await state.set_data(data)


@router.message(F.text, UserState.TASK_ADD_DATE)
async def set_deadline_date(message: Message, state: FSMContext):
    data = await state.get_data()
    data["data_date"] = message.text
    await state.set_data(data)
    await state.set_state(UserState.TASK_ADD_TIME)
    await message.answer(f"Получили дату <i>{data['data_date']}</i>\n\n"
                         f"Введите время дедлайна", parse_mode=ParseMode.HTML)


@router.message(F.text, UserState.TASK_ADD_TIME)
async def set_deadline_time(message: Message, state: FSMContext):
    data = await state.get_data()
    data["data_time"] = message.text
    try:
        await db.add_task(user_id=message.from_user.id,
                          text=data["data_text"],
                          deadline_date=data["data_date"],
                          deadline_time=data["data_time"],
                          reminder_date="pass",
                          reminder_time="pass")
        # добавить подтверждение добавления задачи
        await message.answer(f"Мы сохранили задачу\n"
                             f"<b>{data['data_text']}</b>\n"
                             f"и дедлайн <i>{data['data_date']} {data['data_time']}</i> в целости и сохранности",
                             reply_markup=back_keyboard(),
                             parse_mode=ParseMode.HTML)
    except Exception as e:
        logging.error(e)
        await message.answer(f"Произошла некоторая ошибка, попробуйте ещё раз позже",
                             reply_markup=back_keyboard())
    finally:
        await state.clear()
