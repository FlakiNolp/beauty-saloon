from aiogram.fsm.state import State, StatesGroup


class CurrentTimeTableState(StatesGroup):
    date: State = State()
