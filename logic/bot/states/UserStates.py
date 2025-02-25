from aiogram.fsm.state import State, StatesGroup


class UserState(StatesGroup):
    TASK_TEXT = State()
    TASK_DATE = State()
