from aiogram.fsm.state import StatesGroup, State


class MenuStateForm(StatesGroup):
    choosing_language = State()
    choosing_type = State()
