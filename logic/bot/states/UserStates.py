from aiogram.fsm.state import State, StatesGroup


class UserState(StatesGroup):
    TASK_TEXT = State()
    TASK_DATE = State()
    TASK_PICK = State()
    TASK_MANAGEMENT = State()
