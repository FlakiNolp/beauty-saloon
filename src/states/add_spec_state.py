from aiogram.fsm.state import State, StatesGroup


class AddSpecialistState(StatesGroup):
    names: State = State()
    experience: State = State()
