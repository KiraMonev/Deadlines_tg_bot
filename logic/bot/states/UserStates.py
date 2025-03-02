from aiogram.fsm.state import State, StatesGroup


class UserState(StatesGroup):
    TASK_ADD_TEXT = State()
    TASK_DATE = State()
    TASK_PICK = State()
    TASK_MANAGEMENT = State()
    TASK_CHANGE_TEXT = State()
    TASK_DELETE_ON_DATE = State()
