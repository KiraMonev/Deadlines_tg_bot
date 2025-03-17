from aiogram.fsm.state import State, StatesGroup


class UserState(StatesGroup):
    TASK_ADD_TEXT = State()
    TASK_ADD_DATE = State()
    TASK_ADD_TIME = State()
    TASK_PICK = State()
    TASK_MANAGEMENT = State()
    TASK_CHANGE_TEXT = State()
    TASK_CHANGE_DATE = State()
    TASK_CHANGE_TIME = State()
    TASK_DELETE_ON_DATE = State()
    TASK_ADD_REMINDER_TIME = State()
    TASK_CHANGE_REMINDER_TIME = State()
